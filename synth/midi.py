from core.vqh_interfaces import MappingInterface
import numpy as np
import time
import threading
import queue
from synth.sc import MusicalScale
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MIDIMapping(MappingInterface):
    def __init__(self, output_device=None, bpm=120, quantize_unit=80):
        """
        Initialize MIDI mapping for VQH sonification
        
        Args:
            output_device: Name substring of MIDI output device (None for virtual)
            bpm: Beats per minute for playback
            quantize_unit: MIDI tick quantization unit
        """
        self.output_device = output_device
        self.outport = None
        self.scale = MusicalScale()
        self.bpm = bpm
        self.quantize_unit = quantize_unit
        self.ticks_per_beat = 960
        
        # Real-time playback state
        self.is_playing = False
        self.playback_thread = None
        self.note_queue = queue.Queue()
        self.active_notes = {}  # Track active notes to avoid stuck notes
        
        # MIDI file generation state
        self.current_file = None
        self.current_tracks = {}
        self.note_start_times = {}
        
        self._connect_midi_out()

    def _connect_midi_out(self):
        """Connect to MIDI output device"""
        try:
            if self.output_device:
                # Connect to physical device
                midi_ports = mido.get_output_names()
                matching_ports = [p for p in midi_ports if self.output_device in p]
                
                if matching_ports:
                    self.outport = mido.open_output(matching_ports[0])
                    logger.info(f"Connected to MIDI device: {matching_ports[0]}")
                else:
                    logger.warning(f"No device containing '{self.output_device}' found")
                    self._create_virtual_port()
            else:
                # Create virtual port
                self._create_virtual_port()
                
        except Exception as e:
            logger.error(f"Error connecting to MIDI output: {e}")
            self._create_virtual_port()

    def _create_virtual_port(self):
        """Create virtual MIDI output port"""
        try:
            self.outport = mido.open_output('VQH_MIDI_Out', virtual=True)
            logger.info("Created virtual MIDI port: VQH_MIDI_Out")
        except Exception as e:
            logger.error(f"Could not create virtual MIDI port: {e}")
            self.outport = None

    def realtime_note_mapping(self, data, **kwargs):
        """
        Real-time MIDI note mapping using VQH data structure
        Maps amplitude data to MIDI notes using the current scale
        
        Expected data format: [loudness_dict_list, expect_values, ...]
        """
        if not self.outport:
            logger.error("No MIDI output available")
            return

        loudnesses = data[0]  # First element contains loudness data
        state = loudnesses[0] if isinstance(loudnesses, list) else loudnesses
        
        # Start real-time playback if not already running
        if not self.is_playing:
            self._start_realtime_playback()

        # Convert amplitudes to MIDI notes
        for i, (key, amplitude) in enumerate(state.items()):
            if amplitude > 0.01:  # Threshold for note activation
                note_num = self.scale.get_note(i)
                velocity = int(np.clip(amplitude * 127, 1, 127))
                
                # Queue note for playback
                note_msg = {
                    'type': 'note_on',
                    'note': note_num,
                    'velocity': velocity,
                    'channel': i % 16,  # Distribute across MIDI channels
                    'duration': 0.5  # Default duration
                }
                self.note_queue.put(note_msg)

        logger.debug(f"Queued {len(state)} notes for real-time playback")

    def arpeggio_mapping(self, data, **kwargs):
        """
        Arpeggio-style MIDI mapping similar to note_cluster_intensity_rt
        Plays notes in sequence with timing based on expected values
        """
        if not self.outport:
            logger.error("No MIDI output available")
            return

        loudnesses = data[0]
        expect_values = data[1] if len(data) > 1 else 0
        
        state = loudnesses[0] if isinstance(loudnesses, list) else loudnesses
        
        # Sort by amplitude for arpeggio effect
        sorted_notes = sorted(state.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate timing offset based on expected values
        time_offset = max(0.05, (expect_values + 32) / 400) if hasattr(expect_values, '__float__') else 0.1
        
        # Play notes in sequence
        for i, (key, amplitude) in enumerate(sorted_notes):
            if amplitude > 0.01:
                note_num = self.scale.get_note(i)
                velocity = int(np.clip(amplitude * 127, 1, 127))
                
                # Send immediate note
                self._send_note(note_num, velocity, duration=time_offset * 4)
                time.sleep(time_offset)

    def generate_midi_file(self, data, filename="vqh_output", **kwargs):
        """
        Generate MIDI file from VQH data
        Creates multi-track MIDI file with proper timing
        """
        loudnesses = data[0]
        
        # Create new MIDI file
        mid = MidiFile(ticks_per_beat=self.ticks_per_beat)
        
        # Add tempo track
        tempo_track = MidiTrack()
        tempo_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm), time=0))
        mid.tracks.append(tempo_track)
        
        # Process each time step
        if isinstance(loudnesses, list):
            self._generate_sequence_file(mid, loudnesses, filename)
        else:
            self._generate_single_state_file(mid, loudnesses, filename)
        
        # Save file
        filepath = f"{filename}.mid"
        mid.save(filepath)
        logger.info(f"Saved MIDI file: {filepath}")
        return filepath

    def _generate_sequence_file(self, mid, loudness_sequence, filename):
        """Generate MIDI file from sequence of loudness states"""
        tracks = {}
        time_per_step = self.ticks_per_beat  # One beat per step
        
        for step, state in enumerate(loudness_sequence):
            for i, (key, amplitude) in enumerate(state.items()):
                if amplitude > 0.01:
                    channel = i % 16
                    if channel not in tracks:
                        tracks[channel] = MidiTrack()
                        mid.tracks.append(tracks[channel])
                    
                    note_num = self.scale.get_note(i)
                    velocity = int(np.clip(amplitude * 127, 1, 127))
                    duration = int(time_per_step * 0.8)  # 80% of step duration
                    
                    # Add note on
                    tracks[channel].append(Message('note_on', 
                                                 channel=channel, 
                                                 note=note_num, 
                                                 velocity=velocity, 
                                                 time=time_per_step if step == 0 else 0))
                    
                    # Add note off
                    tracks[channel].append(Message('note_off', 
                                                 channel=channel, 
                                                 note=note_num, 
                                                 velocity=0, 
                                                 time=duration))

    def _generate_single_state_file(self, mid, state, filename):
        """Generate MIDI file from single loudness state"""
        track = MidiTrack()
        mid.tracks.append(track)
        
        note_duration = self.ticks_per_beat
        
        for i, (key, amplitude) in enumerate(state.items()):
            if amplitude > 0.01:
                note_num = self.scale.get_note(i)
                velocity = int(np.clip(amplitude * 127, 1, 127))
                
                # Add simultaneous notes (time=0 after first)
                track.append(Message('note_on', 
                                   channel=0, 
                                   note=note_num, 
                                   velocity=velocity, 
                                   time=0 if i > 0 else 0))
        
        # Add note offs
        for i, (key, amplitude) in enumerate(state.items()):
            if amplitude > 0.01:
                note_num = self.scale.get_note(i)
                track.append(Message('note_off', 
                                   channel=0, 
                                   note=note_num, 
                                   velocity=0, 
                                   time=note_duration if i == 0 else 0))

    def _start_realtime_playback(self):
        """Start real-time MIDI playback thread"""
        if self.playback_thread and self.playback_thread.is_alive():
            return
            
        self.is_playing = True
        self.playback_thread = threading.Thread(target=self._playback_worker, daemon=True)
        self.playback_thread.start()
        logger.info("Started real-time MIDI playback")

    def _playback_worker(self):
        """Worker thread for real-time MIDI playback"""
        while self.is_playing:
            try:
                # Get note from queue with timeout
                note_msg = self.note_queue.get(timeout=0.1)
                
                if note_msg['type'] == 'note_on':
                    self._send_note(note_msg['note'], 
                                  note_msg['velocity'], 
                                  note_msg.get('channel', 0),
                                  note_msg.get('duration', 0.5))
                
                self.note_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Playback error: {e}")

    def _send_note(self, note, velocity, channel=0, duration=0.5):
        """Send a single MIDI note with specified duration"""
        if not self.outport:
            return
            
        try:
            # Send note on
            note_key = (channel, note)
            
            # Stop any existing note on this channel/note
            if note_key in self.active_notes:
                self.outport.send(Message('note_off', channel=channel, note=note, velocity=0))
            
            # Send new note
            self.outport.send(Message('note_on', channel=channel, note=note, velocity=velocity))
            self.active_notes[note_key] = time.time()
            
            # Schedule note off
            def send_note_off():
                time.sleep(duration)
                if self.outport and note_key in self.active_notes:
                    self.outport.send(Message('note_off', channel=channel, note=note, velocity=0))
                    del self.active_notes[note_key]
            
            threading.Thread(target=send_note_off, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error sending MIDI note: {e}")

    def stop_all_notes(self):
        """Stop all currently playing notes"""
        if not self.outport:
            return
            
        for (channel, note) in list(self.active_notes.keys()):
            try:
                self.outport.send(Message('note_off', channel=channel, note=note, velocity=0))
            except:
                pass
        
        self.active_notes.clear()
        
        # Send all notes off control change for safety
        for channel in range(16):
            try:
                self.outport.send(Message('control_change', channel=channel, control=123, value=0))
            except:
                pass

    def set_scale(self, scale_name):
        """Change the musical scale"""
        if scale_name in self.scale.scales:
            self.scale.current_scale = scale_name
            logger.info(f"Changed scale to: {scale_name}")
        else:
            logger.warning(f"Unknown scale: {scale_name}")

    def set_bpm(self, bpm):
        """Change the BPM for playback"""
        self.bpm = bpm
        logger.info(f"Changed BPM to: {bpm}")

    def freeall(self):
        """Stop all playback and clean up resources"""
        self.is_playing = False
        self.stop_all_notes()
        
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)

    def free(self):
        """Stop current playback"""
        self.stop_all_notes()

    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.freeall()
            if self.outport:
                self.outport.close()
        except:
            pass 
