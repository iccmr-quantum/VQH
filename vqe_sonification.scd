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


	snd = Resonz.ar(WhiteNoise.ar(400), freq, 0.0001, [amp1, amp2, amp3, amp4, amp5, amp6, amp7, amp8, amp9, amp10, amp11, amp12]);
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


x =,./. Synth("vqe_model1_son1")

s.quit

71.midicps