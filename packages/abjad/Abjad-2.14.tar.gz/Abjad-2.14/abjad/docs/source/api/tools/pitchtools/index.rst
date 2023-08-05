pitchtools
==========

.. automodule:: abjad.tools.pitchtools

.. only:: html

   Abstract classes
   ----------------

   .. autosummary::

      ~abjad.tools.pitchtools.Interval.Interval
      ~abjad.tools.pitchtools.IntervalClass.IntervalClass
      ~abjad.tools.pitchtools.Pitch.Pitch
      ~abjad.tools.pitchtools.PitchClass.PitchClass
      ~abjad.tools.pitchtools.Segment.Segment
      ~abjad.tools.pitchtools.Set.Set
      ~abjad.tools.pitchtools.Vector.Vector

   Concrete classes
   ----------------

   .. autosummary::

      ~abjad.tools.pitchtools.Accidental.Accidental
      ~abjad.tools.pitchtools.IntervalClassSegment.IntervalClassSegment
      ~abjad.tools.pitchtools.IntervalClassSet.IntervalClassSet
      ~abjad.tools.pitchtools.IntervalClassVector.IntervalClassVector
      ~abjad.tools.pitchtools.IntervalSegment.IntervalSegment
      ~abjad.tools.pitchtools.IntervalSet.IntervalSet
      ~abjad.tools.pitchtools.IntervalVector.IntervalVector
      ~abjad.tools.pitchtools.NamedInterval.NamedInterval
      ~abjad.tools.pitchtools.NamedIntervalClass.NamedIntervalClass
      ~abjad.tools.pitchtools.NamedInversionEquivalentIntervalClass.NamedInversionEquivalentIntervalClass
      ~abjad.tools.pitchtools.NamedPitch.NamedPitch
      ~abjad.tools.pitchtools.NamedPitchClass.NamedPitchClass
      ~abjad.tools.pitchtools.NumberedInterval.NumberedInterval
      ~abjad.tools.pitchtools.NumberedIntervalClass.NumberedIntervalClass
      ~abjad.tools.pitchtools.NumberedInversionEquivalentIntervalClass.NumberedInversionEquivalentIntervalClass
      ~abjad.tools.pitchtools.NumberedPitch.NumberedPitch
      ~abjad.tools.pitchtools.NumberedPitchClass.NumberedPitchClass
      ~abjad.tools.pitchtools.NumberedPitchClassColorMap.NumberedPitchClassColorMap
      ~abjad.tools.pitchtools.Octave.Octave
      ~abjad.tools.pitchtools.OctaveTranspositionMapping.OctaveTranspositionMapping
      ~abjad.tools.pitchtools.OctaveTranspositionMappingComponent.OctaveTranspositionMappingComponent
      ~abjad.tools.pitchtools.OctaveTranspositionMappingInventory.OctaveTranspositionMappingInventory
      ~abjad.tools.pitchtools.PitchClassSegment.PitchClassSegment
      ~abjad.tools.pitchtools.PitchClassSet.PitchClassSet
      ~abjad.tools.pitchtools.PitchClassVector.PitchClassVector
      ~abjad.tools.pitchtools.PitchRange.PitchRange
      ~abjad.tools.pitchtools.PitchRangeInventory.PitchRangeInventory
      ~abjad.tools.pitchtools.PitchSegment.PitchSegment
      ~abjad.tools.pitchtools.PitchSet.PitchSet
      ~abjad.tools.pitchtools.PitchVector.PitchVector
      ~abjad.tools.pitchtools.TwelveToneRow.TwelveToneRow

   Functions
   ---------

   .. autosummary::

      ~abjad.tools.pitchtools.apply_accidental_to_named_pitch.apply_accidental_to_named_pitch
      ~abjad.tools.pitchtools.clef_and_staff_position_number_to_named_pitch.clef_and_staff_position_number_to_named_pitch
      ~abjad.tools.pitchtools.contains_subsegment.contains_subsegment
      ~abjad.tools.pitchtools.get_named_pitch_from_pitch_carrier.get_named_pitch_from_pitch_carrier
      ~abjad.tools.pitchtools.get_numbered_pitch_class_from_pitch_carrier.get_numbered_pitch_class_from_pitch_carrier
      ~abjad.tools.pitchtools.insert_and_transpose_nested_subruns_in_pitch_class_number_list.insert_and_transpose_nested_subruns_in_pitch_class_number_list
      ~abjad.tools.pitchtools.instantiate_pitch_and_interval_test_collection.instantiate_pitch_and_interval_test_collection
      ~abjad.tools.pitchtools.inventory_aggregate_subsets.inventory_aggregate_subsets
      ~abjad.tools.pitchtools.iterate_named_pitch_pairs_in_expr.iterate_named_pitch_pairs_in_expr
      ~abjad.tools.pitchtools.list_named_pitches_in_expr.list_named_pitches_in_expr
      ~abjad.tools.pitchtools.list_numbered_interval_numbers_pairwise.list_numbered_interval_numbers_pairwise
      ~abjad.tools.pitchtools.list_numbered_inversion_equivalent_interval_classes_pairwise.list_numbered_inversion_equivalent_interval_classes_pairwise
      ~abjad.tools.pitchtools.list_octave_transpositions_of_pitch_carrier_within_pitch_range.list_octave_transpositions_of_pitch_carrier_within_pitch_range
      ~abjad.tools.pitchtools.list_ordered_named_pitch_pairs_from_expr_1_to_expr_2.list_ordered_named_pitch_pairs_from_expr_1_to_expr_2
      ~abjad.tools.pitchtools.list_pitch_numbers_in_expr.list_pitch_numbers_in_expr
      ~abjad.tools.pitchtools.list_unordered_named_pitch_pairs_in_expr.list_unordered_named_pitch_pairs_in_expr
      ~abjad.tools.pitchtools.make_n_middle_c_centered_pitches.make_n_middle_c_centered_pitches
      ~abjad.tools.pitchtools.named_pitch_and_clef_to_staff_position_number.named_pitch_and_clef_to_staff_position_number
      ~abjad.tools.pitchtools.numbered_inversion_equivalent_interval_class_dictionary.numbered_inversion_equivalent_interval_class_dictionary
      ~abjad.tools.pitchtools.permute_named_pitch_carrier_list_by_twelve_tone_row.permute_named_pitch_carrier_list_by_twelve_tone_row
      ~abjad.tools.pitchtools.register_pitch_class_numbers_by_pitch_number_aggregate.register_pitch_class_numbers_by_pitch_number_aggregate
      ~abjad.tools.pitchtools.set_written_pitch_of_pitched_components_in_expr.set_written_pitch_of_pitched_components_in_expr
      ~abjad.tools.pitchtools.sort_named_pitch_carriers_in_expr.sort_named_pitch_carriers_in_expr
      ~abjad.tools.pitchtools.spell_numbered_interval_number.spell_numbered_interval_number
      ~abjad.tools.pitchtools.spell_pitch_number.spell_pitch_number
      ~abjad.tools.pitchtools.suggest_clef_for_named_pitches.suggest_clef_for_named_pitches
      ~abjad.tools.pitchtools.transpose_named_pitch_by_numbered_interval_and_respell.transpose_named_pitch_by_numbered_interval_and_respell
      ~abjad.tools.pitchtools.transpose_pitch_carrier_by_interval.transpose_pitch_carrier_by_interval
      ~abjad.tools.pitchtools.transpose_pitch_class_number_to_pitch_number_neighbor.transpose_pitch_class_number_to_pitch_number_neighbor
      ~abjad.tools.pitchtools.transpose_pitch_expr_into_pitch_range.transpose_pitch_expr_into_pitch_range
      ~abjad.tools.pitchtools.transpose_pitch_number_by_octave_transposition_mapping.transpose_pitch_number_by_octave_transposition_mapping
