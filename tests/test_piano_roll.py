import os
import sys
import types
from pathlib import Path
import unittest
from unittest.mock import patch
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from hypothesis import given, settings, strategies as st
from mido import MidiFile, bpm2tempo


class _DummySynth:
    def __init__(self, *args, **kwargs):
        pass


sys.modules.setdefault("fluidsynth", types.SimpleNamespace(Synth=_DummySynth))

UI_ROOT = Path(__file__).resolve().parents[1] / "src" / "Pytone"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from models.note import Note
from models.song import Song
from ui.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from ui.cursor import Cursor
from ui.piano_roll import PianoRoll
from ui.song_ribbon import SongRibbon


pygame.init()


class TestPianoRoll(unittest.TestCase):
    def _make_piano_roll(self) -> PianoRoll:
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        Cursor().init(screen, (255, 255, 255), 2)
        return PianoRoll(
            screen,
            pygame.Rect(64, 64, SCREEN_WIDTH - 64, SCREEN_HEIGHT - 64),
        )

    def _build_visible_note_case(
        self,
        piano_roll: PianoRoll,
        pitch: int,
        start: int,
        duration: int,
    ) -> tuple[Note, pygame.Rect]:
        viewport = pygame.Rect(
            piano_roll.piano_size,
            piano_roll.ribbon_size,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
        )
        note = Note(pitch=pitch, start=start, duration=duration, velocity=100)
        note_rect = piano_roll.get_rect(note)
        self.assertTrue(viewport.colliderect(note_rect))
        return note, note_rect

    @settings(deadline=None, max_examples=25)
    @given(
        pitch=st.integers(min_value=45, max_value=67),
        start=st.integers(min_value=0, max_value=32),
        duration=st.integers(min_value=1, max_value=8),
        x_offset_steps=st.integers(min_value=0, max_value=6),
    )
    def test_right_click_removes_note_under_cursor(
        self,
        pitch: int,
        start: int,
        duration: int,
        x_offset_steps: int,
    ):
        piano_roll = self._make_piano_roll()
        note, note_rect = self._build_visible_note_case(
            piano_roll,
            pitch,
            start,
            duration,
        )
        piano_roll.add_note(note)

        max_x_offset = max(0, note_rect.width - Cursor().size)
        x_offset = min(x_offset_steps * 4, max_x_offset)
        cursor_position = (note_rect.x + x_offset, note_rect.y)

        with patch.object(pygame.mouse, "get_pos", return_value=cursor_position):
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3)
            piano_roll.process(event)

        self.assertEqual(piano_roll.track.note_list, [])

    @settings(deadline=None, max_examples=25)
    @given(
        pitch=st.integers(min_value=45, max_value=67),
        start=st.integers(min_value=0, max_value=32),
        duration=st.integers(min_value=1, max_value=8),
        x_offset_steps=st.integers(min_value=0, max_value=6),
    )
    def test_right_drag_delete_removes_note_under_cursor(
        self,
        pitch: int,
        start: int,
        duration: int,
        x_offset_steps: int,
    ):
        piano_roll = self._make_piano_roll()
        note, note_rect = self._build_visible_note_case(
            piano_roll,
            pitch,
            start,
            duration,
        )
        piano_roll.add_note(note)

        max_x_offset = max(0, note_rect.width - Cursor().size)
        x_offset = min(x_offset_steps * 4, max_x_offset)
        cursor_position = (note_rect.x + x_offset, note_rect.y)

        with patch.object(pygame.mouse, "get_pos", return_value=cursor_position):
            Cursor().holding_right = True
            try:
                event = pygame.event.Event(pygame.MOUSEMOTION)
                piano_roll.process(event)
            finally:
                Cursor().holding_right = False

        self.assertEqual(piano_roll.track.note_list, [])

    def test_song_ribbon_restart_plays_shared_piano_roll_track(self):
        Song.reset_instance()
        try:
            screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            song = Song(bpm=100)
            piano_roll = PianoRoll(
                screen,
                pygame.Rect(64, 64, SCREEN_WIDTH - 64, SCREEN_HEIGHT - 64),
                song=song,
            )
            engine = unittest.mock.Mock()
            song_ribbon = SongRibbon(screen, 64, song=song, engine=engine)
            note = Note(pitch=60, start=0, duration=4, velocity=96)

            piano_roll.add_note(note)
            song_ribbon.tempo.value = 137
            song_ribbon.restart()

            self.assertIs(piano_roll.track, song.track_list[0])
            self.assertEqual(song.track_list[0].note_list, [note])
            self.assertEqual(song.bpm, 137)
            engine.play_midi_async.assert_called_once()

            midi_file = engine.play_midi_async.call_args.args[0]
            self.assertIsInstance(midi_file, MidiFile)

            tempo_messages = [
                message for message in midi_file.tracks[0]
                if message.is_meta and message.type == "set_tempo"
            ]
            self.assertEqual(len(tempo_messages), 1)
            self.assertEqual(tempo_messages[0].tempo, bpm2tempo(137))

            note_messages = [
                message for message in midi_file.tracks[0]
                if not message.is_meta
            ]
            self.assertEqual(
                [message.type for message in note_messages],
                ["program_change", "note_on", "note_off"],
            )
            self.assertEqual(note_messages[1].note, 60)
            self.assertEqual(note_messages[1].velocity, 96)
            self.assertEqual(note_messages[2].time, midi_file.ticks_per_beat)
        finally:
            Song.reset_instance()
