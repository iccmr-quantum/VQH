s.boot
s.quit


(
// Initialize MIDI
MIDIClient.init;
MIDIIn.connectAll;
// MIDIIn.clear

// File path for the JSON

~jsonFilePath = "/home/paulo/QuantumItineraries/VQH/rt_conf.json";
~quboFilePath = "/home/paulo/QuantumItineraries/VQH/midi/qubo_control.json";
// ~filer = File(~jsonFilePath, "r");

)

(
// Function to read JSON file
~readJSON = {
	var file, jsonStr;
    file = File(~jsonFilePath, "r");

    jsonStr = file.readAllString;
    file.close;
	// ~jsonData = jsonStr.parseYAML;
	~jsonData = JSONlib.convertToSC(jsonStr);
	// ~jsonData5.postln;
	~jsonData
};

~writeJSON = {
	var file = File(~jsonFilePath, "w");
	var jsonStr = JSONlib.convertToJSON(~jsonData);
	file.write(jsonStr);
	file.close;
};

~readQUBO = {
	var file, quboStr;
    file = File(~quboFilePath, "r");

    quboStr = file.readAllString;
    file.close;
	// ~jsonData = jsonStr.parseYAML;
	~quboData = JSONlib.convertToSC(quboStr);
	// ~quboData.postln;
	~quboData
};

~writeQUBO = {
	var file = File(~quboFilePath, "w");
	var quboStr = JSONlib.convertToJSON(~quboData);
	file.write(quboStr);
	file.close;
};

)
// ~b = ~readJSON.fork()
~b = ~readQUBO.value
// ~b = ~readJSON.value
// ~writeJSON.fork()
//
// ~b[\clock_speed].class
// ~read.start
// ~jsonData["end"] = false
// ~jsonData.asJSON
// JSONlib.convertToJSON(~jsonData);
//
//
~b[\s1][\s1]


(

~createButtonHandler = { |key, flag, triggval|
	var trigg = triggval;
    { |val, num, chan, src|

		if (val == trigg){
		var state = flag;  // Scale the value
		var data = ~readJSON.value;
		// data.postln;  // Post current state
		data[key] = state;
		// data[key].postln;
		~writeJSON.(data);
		}
    }
};

~createSlideHandler = { |key, minRange, maxRange|
    { |val, num, chan, src|

		var scaledVal = minRange + (val * (maxRange - minRange) / 127).round(0.01);  // Scale the value
		var data = ~readJSON.value;
		// data.postln;  // Post current state
		data[key] = scaledVal;
		// data[key].postln;
		~writeJSON.(data);  // Write changes back to JSON

    }
};

~createQUBOSiderHandler = { |key, minRange, maxRange|
    { |val, num, chan, src|


		var scaledVal = minRange + (val * (maxRange - minRange) / 127).round(0.01);  // Scale the value
		var data = ~readQUBO.value;
		// scaledVal.postln;  // Post current state
		data[key][key] = scaledVal;
		// data[key].postln;
		~writeQUBO.(data);  // Write changes back to JSON

    }
};

~createCouplingSliderHandler = { |key, key2, minRange, maxRange|
    { |val, num, chan, src|


		var scaledVal = minRange + (val * (maxRange - minRange) / 127).round(0.01);  // Scale the value
		var data = ~readQUBO.value;
		// scaledVal.postln;  // Post current state
		data[key][key2] = scaledVal;
		data[key2][key] = scaledVal;
		// data[key].postln;
		~writeQUBO.(data);  // Write changes back to JSON

    }
};

~createQUBOFlipperButton = { |key|
    { |val, num, chan, src|

		if (val == 127){
			var data = ~readQUBO.value;
			var state = data[key][key];
			// data.postln;  // Post current state
			data[key][key] = 1;
			// data[key][key2].postln;
			~writeQUBO.(data);
		};
    };
};

~createQUBOFlipperCoupling = { |key, key2|
    { |val, num, chan, src|

		if (val == 127){
			var data = ~readQUBO.value;
			var state = data[key][key2];
			// data.postln;  // Post current state
			data[key][key2] = 0;
			data[key2][key] = 0;
			// data[key][key2].postln;
			~writeQUBO.(data);
		};
    };
};


~clock_speed_handler = ~createSlideHandler.(\clock_speed, 0.05, 1.0);
~endButtonUp = ~createButtonHandler.(\end, false, 0);
~endButtonDown = ~createButtonHandler.(\end, true, 127);
~nextButton = ~createButtonHandler.(\next_problem, true, 127);
~quboSlider = ~createQUBOSiderHandler.(\s1, -1.0, 1.0);
~quboSlider2 = ~createQUBOSiderHandler.(\s2, -1.0, 1.0);
~quboSlider3 = ~createQUBOSiderHandler.(\s3, -1.0, 1.0);
~quboSlider4 = ~createQUBOSiderHandler.(\s4, -1.0, 1.0);
~quboCoupling12 = ~createCouplingSliderHandler.(\s1, \s2, -1.0, 1.0);
~quboCoupling13 = ~createCouplingSliderHandler.(\s1, \s3, -1.0, 1.0);
~quboCoupling14 = ~createCouplingSliderHandler.(\s1, \s4, -1.0, 1.0);
~quboCoupling23 = ~createCouplingSliderHandler.(\s2, \s3, -1.0, 1.0);
~quboCoupling24 = ~createCouplingSliderHandler.(\s2, \s4, -1.0, 1.0);
~quboCoupling34 = ~createCouplingSliderHandler.(\s3, \s4, -1.0, 1.0);

~quboFlipper1 = ~createQUBOFlipperButton.(\s1);
~quboFlipper2 = ~createQUBOFlipperButton.(\s2);
~quboFlipper3 = ~createQUBOFlipperButton.(\s3);
~quboFlipper4 = ~createQUBOFlipperButton.(\s4);

~quboFlipper12 = ~createQUBOFlipperCoupling.(\s1, \s2);
~quboFlipper13 = ~createQUBOFlipperCoupling.(\s1, \s3);
~quboFlipper14 = ~createQUBOFlipperCoupling.(\s1, \s4);
~quboFlipper23 = ~createQUBOFlipperCoupling.(\s2, \s3);
~quboFlipper24 = ~createQUBOFlipperCoupling.(\s2, \s4);
~quboFlipper34 = ~createQUBOFlipperCoupling.(\s3, \s4);
)

a = MIDIFunc.cc({arg ...args; args.postln});
a.free;
(
~s0 = MIDIFunc.cc(~quboSlider, [0], [0]);
~s5 = MIDIFunc.cc(~quboSlider2, [5], [0]);
~s10 = MIDIFunc.cc(~quboSlider3, [10], [0]);
~s15 = MIDIFunc.cc(~quboSlider4, [15], [0]);

~s1 = MIDIFunc.cc(~quboCoupling12, [1], [0]);
~s2 = MIDIFunc.cc(~quboCoupling13, [2], [0]);
~s3 = MIDIFunc.cc(~quboCoupling14, [3], [0]);
~s6 = MIDIFunc.cc(~quboCoupling23, [6], [0]);
~s7 = MIDIFunc.cc(~quboCoupling24, [7], [0]);
~s11 = MIDIFunc.cc(~quboCoupling34, [11], [0]);

~f0 = MIDIFunc.cc(~quboFlipper1, [0], [1]);
~f5 = MIDIFunc.cc(~quboFlipper2, [5], [1]);
~f10 = MIDIFunc.cc(~quboFlipper3, [10], [1]);
~f15 = MIDIFunc.cc(~quboFlipper4, [15], [1]);

~f1 = MIDIFunc.cc(~quboFlipper12, [1], [1]);
~f2 = MIDIFunc.cc(~quboFlipper13, [2], [1]);
~f3 = MIDIFunc.cc(~quboFlipper14, [3], [1]);
~f6 = MIDIFunc.cc(~quboFlipper23, [6], [1]);
~f7 = MIDIFunc.cc(~quboFlipper24, [7], [1]);
~f11 = MIDIFunc.cc(~quboFlipper34, [11], [1]);


~b0d = MIDIFunc.cc(~nextButton, [12], [1]);
// ~b0u = MIDIFunc.cc(~buttonUp, [0], [1]);
~t0 = MIDIFunc.cc(~clock_speed_handler, [12], [0]);
~b28d = MIDIFunc.cc(~endButtonDown, [28], [1]);
~b28u = MIDIFunc.cc(~endButtonUp, [28], [1]);
)


(
~b0d.free;

~s0.free;
~s5.free;
~s10.free;
~s15.free;

~s1.free;
~s2.free;
~s3.free;
~s6.free;
~s7.free;
~s11.free;


~f0.free;
~f5.free;
~f10.free;
~f15.free;

~f1.free;
~f2.free;
~f3.free;
~f6.free;
~f7.free;
~f11.free;

// ~b0u.free;
~t0.free;
~b28d.free;
~b28u.free;
)

(
~cmd = "python3 /home/paulo/QuantumItineraries/VQH/control_to_setup.py";
var process;

// Check if Python 3 needs to be specified explicitly
// var cmd = "python3 /path/to/test_script.py";

~cmd.unixCmd;

)










//Quarks.install("https://github.com/musikinformatik/JSONlib.git");
// thisProcess.recompile;