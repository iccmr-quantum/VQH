s.boot
s.quit

s.options.numOutputBusChannels = 4;
s.scope(zoom:4)

~viola = Buffer.read(s, Platform.resourceDir +/+ "sounds/a11wlk01.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_1_click_original.wav");
~viola = Buffer.read(s, "RS_SC_sounds/Ryu_Jin_Selected1_Treated.wav");
~viola = Buffer.read(s, "RS_SC_sounds/Ryu_Jin_Selected2_Treated.wav");
~viola = Buffer.read(s, "RS_SC_sounds/Ryu_Jin_Selected3_Treated.wav");
~viola = Buffer.read(s, "RS_SC_sounds/Ryu_Jin_Selected4_Treated.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_3_Sweep_4.wav");
~viola = Buffer.read(s, "RS_SC_sounds/Mono_RJ_4_click_single_band_100l.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_1_SG_Harmonic2Fold_2.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_2_SR_Fold2Harmonic.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_4_Fold2Harmonic2Fold.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_2_Deconstruct_2_Tonal_p3_1.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_1_bird.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_2_SR_Fold2Harmonic.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_2_SR_Fold2Harmonic.wav");
~viola = Buffer.read(s, "RS_SC_sounds/RJ_2_SR_Fold2Harmonic.wav");
~viola.play;

//Test
(SynthDef(\vqgrains, {|out=0, s0=1, s1=1, s2=1, s3=1|
    var trate, dur, clk, pos, pan, sig;
    //trate = MouseY.kr(8,120,1);
    trate = 20;
	dur = 12 / trate;
	clk = Impulse.kr([s0*trate, s1*trate, s2*trate, s3*trate]);
    pos = MouseX.kr(0,BufDur.kr(~viola.bufnum)) + TRand.kr(0, 0.01, clk);
    pan = WhiteNoise.kr(0.6);
    sig = TGrains.ar(4, clk, ~viola.bufnum, 1, pos, dur, pan, 0.3);

	Out.ar(out, sig);
}).store;
)

(SynthDef(\vqgrains, {|out=0, s0=1, s1=1, s2=1, s3=1, rate=1|
    var trate, dur, clk, pos, pan, sig;
    //trate = MouseY.kr(8,120,1);
    trate = rate;
	dur = 12 / trate;
	// clk = Impulse.kr([trate, trate, trate, trate]);
	clk = Impulse.kr([s0*trate, s1*trate, s2*trate, s3*trate]);
    //pos = MouseX.kr(0,BufDur.kr(~viola)) + TRand.kr(0, 0.01, clk);
	pos = [s0, s1, s2, s3]*BufDur.kr(~viola.bufnum);
	pan = WhiteNoise.kr(0.6);
	sig = TGrains.ar(4, clk, ~viola.bufnum, rate, pos, dur, pan, 0.3);
	// sig = TGrains.ar(4, clk, ~viola.bufnum, 1, pos, dur, pan, 0.3);

	Out.ar(out, sig);
}).store;
)

(SynthDef(\vqgrains_rt, {|out=0, amp1=1, amp2=1, amp3=1, amp4=1, rate=1|
    var trate, dur, clk, pos, pan, sig;
    //trate = MouseY.kr(8,120,1);
    trate = rate;
	dur = 12 / trate;
	// clk = Impulse.kr([trate, trate, trate, trate]);
	clk = Impulse.kr([amp1*trate, amp2*trate, amp3*trate, amp4*trate]);
    //pos = MouseX.kr(0,BufDur.kr(~viola)) + TRand.kr(0, 0.01, clk);
	pos = [amp1, amp2, amp3, amp4]*BufDur.kr(~viola.bufnum);
	pan = WhiteNoise.kr(0.6);
	sig = TGrains.ar(4, clk, ~viola.bufnum, rate, pos, dur, pan, 0.3);
	// sig = TGrains.ar(4, clk, ~viola.bufnum, 1, pos, dur, pan, 0.3);

	Out.ar(out, sig);
}).store;
)

Buffer.freeAll

x =Synth("vqgrains")
Slew

x.set(\s0, 0.2)


//--- Recording
(
~subdir="Recordings/";
~path=thisProcess.nowExecutingPath.dirname +/+ ~subdir;

)

~name = "vqe_Session_RS_Quad_run29_1_6_foldharmfold_highrate_quad";
s.prepareForRecord(~path++"sc_"++~name.asString++".wav", 4);

s.record;
s.stopRecording;

PanAz

// 4 channels
(
{
    var trate, dur, clk, pos, pan;
    trate = MouseY.kr(8,120,1);
    dur = 12 / trate;
    clk = Impulse.kr(trate);
    pos = MouseX.kr(0,BufDur.kr(~viola)) + TRand.kr(0, 0.01, clk);
    pan = WhiteNoise.kr(0.6);
    TGrains.ar(4, clk, ~viola, 1, pos, dur, pan, 0.1);
}.play;
)


d = ProxySynthDef("test", { arg freq=440; 0.1*SinOsc.ar(freq) }).store;
x = Synth("test", [\freq, 340])
x.set(\fadeTime, 4)
x.set(\freq, 500)
s.sendMsg("/s_new", "test", 1980, 1, 1, \freq, 340);
s.sendMsg("/n_set", 1980, \freq, 240);
s.sendMsg("/n_set", 1980, \fadeTime, 4);
s.sendMsg("/n_set", 1980, \gate, 0);

(
SynthDef.new("example 6", {arg out = 0, freq = 440, amp = 0.2,
gate = 1, a, d, s, r;
var env, sin, slew;
env = EnvGen.kr(Env.adsr(a, d, s, r, amp), gate);
//slew = Slew.kr(freq, 1, 1);
slew = Lag2.kr(freq, 0.9);
sin = SinOsc.ar(slew, mul:env);
Out.ar(out, sin);
}).send(s);
)
a = Synth.new("example 6", [\freq, 440, \a, 0.2, \d, 0.1, \s, 0.9, \r, 0.5, \gate, 1]);
a.set(\freq, 587);
a.set(\freq, 330);
a.set(\gate, 0);