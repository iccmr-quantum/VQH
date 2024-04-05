s.boot
s.quit
MIDIClient.init;
MIDIIn.connectAll;
(
// Set the target number of messages
~targetMessages = 3;

// Counter to keep track of received messages
~messageCounter = 0;
~messagecoulterl = [nil, nil, nil];
// Callback function to be triggered when all messages arrive
(
~allMessagesReceivedCallback = {
	var k;
	"------------------".postln;
	~messagecoulterl.postln;
	// (~messagecoulterl[0]/8).postln;
	// "All three messages received!".postln;
	~h = File("~/QuantumItineraries/VQH/display_hexagonal_chambers/data/time.dat".standardizePath, "w");
	3.do({|i| ~h.putInt8(~messagecoulterl[i]);});
	~h.close;
    // Your additional processing code here
};
);
(
// Update processing function
~updateProcessing = {|...args|
	// args[0].postln;
	// args[1].postln;
	// args.postln;
    // Increment the counter
	if (~messagecoulterl[args[1]-1] == nil, {
		~messageCounter = ~messageCounter + 1;
		~messagecoulterl[args[1]-1] = args[0];
	});
	// Check if all messages have been received
    if (~messageCounter >= ~targetMessages) {
        // Call the callback function
        ~allMessagesReceivedCallback.value;
		~messagecoulterl = [nil, nil, nil];
        // Reset the counter for the next round of messages
        ~messageCounter = 0;
    }
};
);
b = MIDIFunc.cc(~updateProcessing, (1..3), 9)
// b.free;

)
b.free
(
//Reset

~messageCounter = 0
~messagecoulterl = [nil, nil, nil];

)


(
//Test
var k;
~h = File("~/QuantumItineraries/VQH/display_hexagonal_chambers/data/time.dat".standardizePath, "w");
k = [100, 12];
k.size.postln;
k.size.do({|i| ~h.putInt8(k[i]); });
~h.close;
)

(
if ( [false, true].choose,                // Boolean expression (chooses one at random)
    { "expression was true".postln },    // true function
    { "expression was false".postln }    // false function
)
)