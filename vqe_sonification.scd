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

x =,./. Synth("vqe_model1_son1")

s.quit

71.midicps