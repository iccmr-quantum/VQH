s.boot

(
SynthDef(\mel_fb_dif1, { |out=0, gain=0.5, bufnum=0, inbufnum=12, amp1=0.1, amp2=0.1, amp3=0.1, amp4=0.1, amp5=0.1, amp6=0.1, amp7=0.1, amp8=0.1, amp9=0.1, amp10=0.1, amp11=0.1, amp12=0.1|
	var in, chainIn, chainOut, bands=12, buffers, sig;


	//in = WhiteNoise.ar(0.4);
	//in = LFSaw.ar(MouseY.kr(100, 1000, 1), 0, 0.2);
	in = PlayBuf.ar(1, inbufnum, doneAction:2);

	buffers = Array.fill(bands,{|i| i + bufnum });

	chainIn = FFT(LocalBuf(1024!bands), in!bands*[amp1, amp2, amp3, amp4, amp5, amp6, amp7, amp8, amp9, amp10, amp11, amp12]);

	chainOut = PV_MagMul(chainIn, buffers);


	sig = (IFFT(chainOut));

	Out.ar(out, sig*gain!2);

}).store;
)



Synth("mel_fb_dif1", [\bufnum,~hh[0].bufnum, \inbufnum, ~viola.bufnum])



~hh = Buffer.allocConsecutive(12, s, 1024);

~viola = Buffer.read(s, "VA_R42_c_LevadonaEstalo.wav")
~viola = Buffer.read(s, "VA_K122_v_Viola_e_voz01.wav")
~viola.play

12.do({|i| ~hh[i].read("melfb"++i++".wav").postln;})

~hh[0].plot
~hh[0].zero
~hh[0].set(512, 1)

~hh[0].bufnum
~viola.bufnum

{TRand.kr(0,BufDur.kr(15))}.value

// Decoupled version

(
SynthDef(\input_signal, { |out=0, bufnum=0, amp=1, rate=1|
	var sig;

	sig = PlayBuf.ar(1, bufnum, doneAction:2);

	Out.ar(out, sig*amp);
}).store;

SynthDef(\input_signal2, { |out=0, bufnum=0, amp=1, rate=1|
	var sig, env;

	env = EnvGen.ar(Env.perc(0.01, 0.02, amp), doneAction:2);
	sig = WhiteNoise.ar(0.25);

	Out.ar(out, sig*env);
}).store;

SynthDef(\input_signal3, { |out=0, bufnum=0, amp=1, rate=1, pos=2.1, dur=0.4, tgrate=10|
	var sig, env, tdur, trate;

	//env = EnvGen.ar(Env.new([0, 1], dur), doneAction:2);
	//trate = MouseY.kr(2,200,1);
	trate = tgrate;
	tdur = 4 / trate;
	env = EnvGen.ar(Env.new([0, 1], dur), doneAction:2);
	//sig = TGrains.ar(1, Impulse.ar(trate), bufnum, rate, MouseX.kr(0,BufDur.kr(bufnum)), tdur);
	//sig = TGrains.ar(1, Impulse.ar(trate), bufnum, tgrate/20, TRand.kr(0,BufDur.kr(bufnum), Impulse.kr(trate)), tdur);
	sig = TGrains.ar(1, Impulse.ar(trate), bufnum, rate, tgrate/20, tdur);
	//sig = sig + WhiteNoise.ar(0.25);
	Out.ar(out, sig);
}).store;


SynthDef(\mel_fb_dif2, { |out=0, inbus=1, gain=0.5, bufnum=0, inbufnum=12, amp1=0.1, amp2=0.1, amp3=0.1, amp4=0.1, amp5=0.1, amp6=0.1, amp7=0.1, amp8=0.1, amp9=0.1, amp10=0.1, amp11=0.1, amp12=0.1|
	var in, chainIn, chainOut, bands=12, buffers, sig;

	in = In.ar(inbus, 1);
	//in = WhiteNoise.ar(0.4);
	//in = LFSaw.ar(MouseY.kr(100, 1000, 1), 0, 0.2);
	//in = PlayBuf.ar(1, inbufnum, doneAction:2);

	buffers = Array.fill(bands,{|i| i + bufnum });

	chainIn = FFT(LocalBuf(1024!bands), in!bands*[amp1, amp2, amp3, amp4, amp5, amp6, amp7, amp8, amp9, amp10, amp11, amp12]);

	chainOut = PV_MagMul(chainIn, buffers);


	sig = (IFFT(chainOut));

	Out.ar(out, sig*gain!2);

}).store;
)

(
~srcGroup = Group.new;
~fxGroup = Group.after(~srcGroup);
~srcBus = Bus.audio(s, 1);
)

x = Synth(\mel_f
	b_dif2, [\inbus, ~srcBus], ~fxGroup.nodeID)
x = Synth(\input_signal, [\bufnum, 17, \out, ~srcBus.index], ~srcGroup.nodeID)

~fxGroup.nodeID
~srcBus.index



// =================== TESTS & EXPERIMENTS ======================= //
~hh = Buffer.allocConsecutive(5, s, 1024);

5.do({|i| ~hh[i].read("melfb"++i++".wav").postln;})

~hh[4].plot


FreqScope.new(400, 500, server: s);

(
{
	var inA, chainA, inB, chainB, chain, chain2;
	//inA = LFSaw.ar(MouseY.kr(100, 1000, 1), 0, 0.2);
	inA = WhiteNoise.ar(0.4);

        chainA = FFT(LocalBuf(1024), inA);

	chain = PV_MagMul(chainA, ~hh[1]);// writes into bufferA
	chain2 = PV_MagMul(chainA, ~hh[4]);
	IFFT(chain) * 0.1 + IFFT(chain2)*0.1;
	//IFFT(chain)*0.1
}.play;
)

(
SynthDef(\mel_fb_dif_test, { |out=0, gain=1, bufnum=0|
	var in, chain_in, chain1, chain2, sig;

	in = WhiteNoise.ar(0.4);

        chain_in = FFT(LocalBuf(1024), in);

	chain1 = PV_MagMul(chain_in, bufnum);// writes into bufferA
	//chain2 = PV_MagMul(chain_in, ~hh[4]);

	sig = (IFFT(chain1)*0.2);
	//sig = sig + (IFFT(chain2)*0.1);

	Out.ar(out, sig*gain!2);
}).store;
)

Array.fill(4, { |i|; i * 2 })
4.do({|i| i.postln;})
Synth("mel_fb_dif1", [\bufnum,47])

(
SynthDef(\env_help, { | out, gate = 0, freq = 440, doneAction = 0 |
    var z = EnvGen.kr(Env.perc(0.004, 3, 0.5), gate, doneAction: doneAction) * SinOsc.ar(freq, 0, 0.1);
    Out.ar(out, z)
}).add;
)

a = Synth(\env_help);


// turn on
a.set(\gate, 1);

// turn off
a.set(\gate, 0);

// it does not matter to what value the gate is set, as long as it is > 0
a.set(\gate, 2);

a.set(\doneAction, 2, \gate, 0); // set doneAction to two to let the synth free itself

a.free; // alternatively, free it directly.


~viola = Buffer.read(s, Platform.resourceDir +/+ "sounds/a11wlk01.wav");
~viola.play;
(
{
    var trate, dur, rate;
    trate = MouseY.kr(2,200,1);
    dur = 4 / trate;
    rate = Dseq([10, 1, 1, 0.5, 0.5, 0.2, 0.1], inf);
    TGrains.ar(2, Impulse.ar(trate), ~viola, rate, MouseX.kr(0,BufDur.kr(~viola)), dur, Dseq([-1, 1], inf), 0.1, 2);
}.scope(zoom: 4);
)