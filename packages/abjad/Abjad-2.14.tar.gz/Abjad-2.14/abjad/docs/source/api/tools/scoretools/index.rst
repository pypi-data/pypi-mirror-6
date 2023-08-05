scoretools
==========

.. automodule:: abjad.tools.scoretools

.. only:: html

   Abstract classes
   ----------------

   .. autosummary::

      ~abjad.tools.scoretools.Component.Component
      ~abjad.tools.scoretools.Leaf.Leaf

   Concrete classes
   ----------------

   .. autosummary::

      ~abjad.tools.scoretools.Chord.Chord
      ~abjad.tools.scoretools.Cluster.Cluster
      ~abjad.tools.scoretools.Container.Container
      ~abjad.tools.scoretools.Context.Context
      ~abjad.tools.scoretools.FixedDurationContainer.FixedDurationContainer
      ~abjad.tools.scoretools.FixedDurationTuplet.FixedDurationTuplet
      ~abjad.tools.scoretools.GraceContainer.GraceContainer
      ~abjad.tools.scoretools.GrandStaff.GrandStaff
      ~abjad.tools.scoretools.Measure.Measure
      ~abjad.tools.scoretools.MultimeasureRest.MultimeasureRest
      ~abjad.tools.scoretools.Note.Note
      ~abjad.tools.scoretools.NoteHead.NoteHead
      ~abjad.tools.scoretools.NoteHeadInventory.NoteHeadInventory
      ~abjad.tools.scoretools.PianoStaff.PianoStaff
      ~abjad.tools.scoretools.Rest.Rest
      ~abjad.tools.scoretools.RhythmicStaff.RhythmicStaff
      ~abjad.tools.scoretools.Score.Score
      ~abjad.tools.scoretools.Skip.Skip
      ~abjad.tools.scoretools.Staff.Staff
      ~abjad.tools.scoretools.StaffGroup.StaffGroup
      ~abjad.tools.scoretools.Tuplet.Tuplet
      ~abjad.tools.scoretools.Voice.Voice

   Functions
   ---------

   .. autosummary::

      ~abjad.tools.scoretools.append_spacer_skip_to_underfull_measure.append_spacer_skip_to_underfull_measure
      ~abjad.tools.scoretools.append_spacer_skips_to_underfull_measures_in_expr.append_spacer_skips_to_underfull_measures_in_expr
      ~abjad.tools.scoretools.apply_full_measure_tuplets_to_contents_of_measures_in_expr.apply_full_measure_tuplets_to_contents_of_measures_in_expr
      ~abjad.tools.scoretools.extend_measures_in_expr_and_apply_full_measure_tuplets.extend_measures_in_expr_and_apply_full_measure_tuplets
      ~abjad.tools.scoretools.fill_measures_in_expr_with_full_measure_spacer_skips.fill_measures_in_expr_with_full_measure_spacer_skips
      ~abjad.tools.scoretools.fill_measures_in_expr_with_minimal_number_of_notes.fill_measures_in_expr_with_minimal_number_of_notes
      ~abjad.tools.scoretools.fill_measures_in_expr_with_repeated_notes.fill_measures_in_expr_with_repeated_notes
      ~abjad.tools.scoretools.fill_measures_in_expr_with_time_signature_denominator_notes.fill_measures_in_expr_with_time_signature_denominator_notes
      ~abjad.tools.scoretools.get_measure_that_starts_with_container.get_measure_that_starts_with_container
      ~abjad.tools.scoretools.get_measure_that_stops_with_container.get_measure_that_stops_with_container
      ~abjad.tools.scoretools.get_next_measure_from_component.get_next_measure_from_component
      ~abjad.tools.scoretools.get_one_indexed_measure_number_in_expr.get_one_indexed_measure_number_in_expr
      ~abjad.tools.scoretools.get_previous_measure_from_component.get_previous_measure_from_component
      ~abjad.tools.scoretools.make_empty_piano_score.make_empty_piano_score
      ~abjad.tools.scoretools.make_leaves.make_leaves
      ~abjad.tools.scoretools.make_leaves_from_talea.make_leaves_from_talea
      ~abjad.tools.scoretools.make_multimeasure_rests.make_multimeasure_rests
      ~abjad.tools.scoretools.make_multiplied_quarter_notes.make_multiplied_quarter_notes
      ~abjad.tools.scoretools.make_notes.make_notes
      ~abjad.tools.scoretools.make_notes_with_multiplied_durations.make_notes_with_multiplied_durations
      ~abjad.tools.scoretools.make_percussion_note.make_percussion_note
      ~abjad.tools.scoretools.make_piano_score_from_leaves.make_piano_score_from_leaves
      ~abjad.tools.scoretools.make_piano_sketch_score_from_leaves.make_piano_sketch_score_from_leaves
      ~abjad.tools.scoretools.make_repeated_notes.make_repeated_notes
      ~abjad.tools.scoretools.make_repeated_notes_from_time_signature.make_repeated_notes_from_time_signature
      ~abjad.tools.scoretools.make_repeated_notes_from_time_signatures.make_repeated_notes_from_time_signatures
      ~abjad.tools.scoretools.make_repeated_notes_with_shorter_notes_at_end.make_repeated_notes_with_shorter_notes_at_end
      ~abjad.tools.scoretools.make_repeated_rests_from_time_signatures.make_repeated_rests_from_time_signatures
      ~abjad.tools.scoretools.make_repeated_skips_from_time_signatures.make_repeated_skips_from_time_signatures
      ~abjad.tools.scoretools.make_rests.make_rests
      ~abjad.tools.scoretools.make_rhythmic_sketch_staff.make_rhythmic_sketch_staff
      ~abjad.tools.scoretools.make_skips_with_multiplied_durations.make_skips_with_multiplied_durations
      ~abjad.tools.scoretools.make_spacer_skip_measures.make_spacer_skip_measures
      ~abjad.tools.scoretools.make_tied_leaf.make_tied_leaf
      ~abjad.tools.scoretools.move_full_measure_tuplet_prolation_to_measure_time_signature.move_full_measure_tuplet_prolation_to_measure_time_signature
      ~abjad.tools.scoretools.move_measure_prolation_to_full_measure_tuplet.move_measure_prolation_to_full_measure_tuplet
      ~abjad.tools.scoretools.replace_contents_of_measures_in_expr.replace_contents_of_measures_in_expr
      ~abjad.tools.scoretools.scale_measure_denominator_and_adjust_measure_contents.scale_measure_denominator_and_adjust_measure_contents
      ~abjad.tools.scoretools.set_always_format_time_signature_of_measures_in_expr.set_always_format_time_signature_of_measures_in_expr
      ~abjad.tools.scoretools.set_measure_denominator_and_adjust_numerator.set_measure_denominator_and_adjust_numerator
