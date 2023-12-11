s.boot;

(
SynthDef(\vqe_model1_son1, {|out, freq=#[261.6255653006, 277.18263097687, 293.66476791741, 311.12698372208, 329.62755691287, 349.228231433, 369.99442271163, 391.99543598175, 415.30469757995, 440.0, 466.16376151809, 493.88330125612], amp1=0.1, amp2=0.1, amp3=0.1, amp4=0.1, amp5=0.1, amp6=0.1, amp7=0.1, amp8=0.1, amp9=0.1, amp10=0.1, amp11=0.1, amp12=0.1, gain=0.5| var env, snd;


	// Percussive envelope == Percussive attack sound
	/*env = EnvGen.ar(Env.perc(0.05, 1, 0.2), doneAction:0);*/
	env = EnvGen.ar(Env.new([0, 0.1], 1), doneAction:0);


	//snd = Resonz.ar(WhiteNoise.ar(0.2), freqs, 0.02, amps);
	snd = SinOsc.ar(freq, mul: [amp1, amp2, amp3, amp4, amp5, amp6, amp7, amp8, amp9, amp10, amp11, amp12]);

	snd = snd*env;

	snd=snd*gain;

	// Output
	Out.ar(out, (snd)!2)
}).store;

SynthDescLib.global[\vqe_model1_son1]
)

Synth(\vqe_model1_son1)
(
SynthDef(\vqe_model1_son1, {|out, freq=#[261.6255653006, 277.18263097687, 293.66476791741, 311.12698372208, 329.62755691287, 349.228231433, 369.99442271163, 391.99543598175, 415.30469757995, 440.0, 466.16376151809, 493.88330125612], amp1=0.1, amp2=0.1, amp3=0.1, amp4=0.1, amp5=0.1, amp6=0.1, amp7=0.1, amp8=0.1, amp9=0.1, amp10=0.1, amp11=0.1, amp12=0.1, gain=0.5| var env, snd;


	// Percussive envelope == Percussive attack sound
	/*env = EnvGen.ar(Env.perc(0.05, 1, 0.2), doneAction:0);*/
	env = EnvGen.ar(Env.new([0, 0.1], 1), doneAction:0);


	snd = Resonz.ar(WhiteNoise.ar(400), freq/2, 0.0001, [amp1, amp2, amp3, amp4, amp5, amp6, amp7, amp8, amp9, amp10, amp11, amp12]);
	//snd = SinOsc.ar(freq, mul: [amp1, amp2, amp3, amp4, amp5, amp6, amp7, amp8, amp9, amp10, amp11, amp12]);

	snd = snd*env;

	snd=snd*gain;

	// Output
	Out.ar(out, (snd)!2)
}).store;

SynthDescLib.global[\vqe_model1_son1]
)


(
SynthDef(\vqe_son2, {|out, note=0, amp=0.1| var env, snd, freq;


	env = EnvGen.ar(Env.perc(0.004, 0.31, 0.5), doneAction:Done.freeSelf);

	freq = note.midicps;

	snd = LFCub.ar([freq, 3.4*freq, 4.5*freq, 7.5*freq], mul: [amp, 0.4*amp, 0.1*amp, 0.08*amp]);


	snd = snd*env;

	snd=snd*0.5;

	// Output
	Out.ar(out, ((snd))!2)
}).store;
)
476.8*2
(
SynthDef(\vqe_son3, {|out, freq=#[3206.0, 1029.6, 1620.0, 2322.0, 2699, 7113.0, 1907.2, 2869, 3057.0, 3460.0, 5021.0, 5288.0], amp1=0.1, amp2=0.1, amp3=0.1, amp4=0.1, amp5=0.1, amp6=0.1, amp7=0.1, amp8=0.1, amp9=0.1, amp10=0.1, amp11=0.1, amp12=0.1, gain=0.05, shift=0| var env, snd;


	// Percussive envelope == Percussive attack sound
	/*env = EnvGen.ar(Env.perc(0.05, 1, 0.2), doneAction:0);*/
	env = EnvGen.ar(Env.new([0, 0.1], 1), doneAction:0);


	snd = DynKlank.ar(`[freq - Lag.kr((10*shift), 0.3), Lag.kr([amp1, amp2, amp3, amp4, amp5, amp6, amp7, amp8, amp9, amp10, amp11, amp12], 0.6), [0.5]], BrownNoise.ar(0.1));
	//snd = DynKlank.ar(`[freq, [amp1, amp2, amp3, amp4, amp5, amp6, amp7, amp8, amp9, amp10, amp11, amp12], [1]], BrownNoise.ar(0.1));
	//snd = SinOsc.ar(freq, mul: [amp1, amp2, amp3, amp4, amp5, amp6, amp7, amp8, amp9, amp10, amp11, amp12]);

	snd = snd*env;

	snd=snd*gain;

	// Output
	Out.ar(out, (snd)!2)
}).store;

//SynthDescLib.global[\vqe_model1_son1]
)
p.fadeTime=0.3

s.quit

//--- Recording
(
~subdir="Recordings/";
~path=thisProcess.nowExecutingPath.dirname +/+ ~subdir;

)

~name = "vqe_Saber_run10_3_5";
s.prepareForRecord(~path++"sc_"++~name.asString++".wav");

s.record;
s.stopRecording;

(
{1.do{|i| var z;
	// Duration in seconds

	~note=i;
	if(i<=9, {z = "0"}, {z = ""});
	// File name
	s.prepareForRecord(~path++"_"++~name.asString++".wav");
	0.5.wait;

	s.record;
	0.2.wait;
	~seq.start;
	0.5.wait;
	~dur=~duration+3;
	~dur.wait;

	s.stopRecording;
	0.5.wait;
}
}.fork;

)


71.midicps