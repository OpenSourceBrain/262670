#!/usr/bin/env python3
"""
Post process and add biophysics to cells.

We make any updates to the morphology, and add biophysics.

File: NeuroML2/postprocess_cells.py

Copyright 2022 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import random

import neuroml
from neuroml.loaders import read_neuroml2_file
from pyneuroml.pynml import write_neuroml2_file
from neuroml.utils import component_factory

random.seed(1412)


def load_and_setup_cell(cellname: str):
    """Load a cell, and clean it to prepare it for further modifications.

    These operations are common for all cells.

    :param cellname: name of cell.
        the file containing the cell should then be <cell>.morph.cell.nml
    :returns: document with cell
    :rtype: neuroml.NeuroMLDocument

    """
    celldoc = read_neuroml2_file(
        f"{cellname}.morph.cell.nml"
    )  # type: neuroml.NeuroMLDocument
    cell = celldoc.cells[0]  # type: neuroml.Cell
    celldoc.networks = []
    cell.id = cellname
    cell.notes = cell.notes.replace("GGN_20170309_sc_0_0", cellname)
    cell.notes += ". Reference: Subhasis Ray, Zane N Aldworth, Mark A Stopfer (2020) Feedback inhibition and its control in an insect olfactory circuit eLife 9:e53281."

    [
        default_all_group,
        default_soma_group,
        default_dendrite_group,
        default_axon_group,
    ] = cell.setup_default_segment_groups(
        use_convention=True,
        default_groups=["all", "soma_group", "dendrite_group", "axon_group"],
    )

    # populate default groups
    for sg in cell.morphology.segment_groups:
        if "soma" in sg.id and sg.id != "soma_group":
            default_soma_group.add(neuroml.Include(segment_groups=sg.id))
        if "axon" in sg.id and sg.id != "axon_group":
            default_axon_group.add(neuroml.Include(segment_groups=sg.id))
        if "dend" in sg.id and sg.id != "dendrite_group":
            default_dendrite_group.add(neuroml.Include(segment_groups=sg.id))

    cell.optimise_segment_groups()

    return celldoc


def postprocess_GGN():
    """Post process GGN and add biophysics."""
    cellname = "GGN"
    celldoc = load_and_setup_cell(cellname)
    cell = celldoc.cells[0]  # type: neuroml.Cell

    # biophysics
    # all
    cell.add_channel_density(
        nml_cell_doc=celldoc,
        cd_id="pas",
        ion_channel="pas",
        cond_density="0.00003 S_per_cm2",
        erev="-51 mV",
        group_id="all",
        ion="non_specific",
        ion_chan_def_file="channels/pas.channel.nml",
    )
    cell.set_resistivity("0.1 kohm_cm", group_id="all")
    cell.set_specific_capacitance("1 uF_per_cm2", group_id="all")
    cell.set_init_memb_potential("-80mV")

    # L1 validation
    # cell.validate(recursive=True)
    cell.summary(morph=False, biophys=True)
    # use pynml writer to also run L2 validation
    write_neuroml2_file(celldoc, f"{cellname}.cell.nml")


def postprocess_KC():
    """Manually create KC and add biophysics."""
    celldoc = component_factory("NeuroMLDocument", id="KC_doc")  # type: neuroml.NeuroMLDocument
    cell = celldoc.add("Cell", id="KC", validate=False)  # type: neuroml.Cell
    cell.setup_nml_cell()
    cell.add_segment([0, 0, 0, 20], [0, 0, 6.366, 20], seg_type="soma")

    # biophysics
    # all
    cell.add_channel_density(
        nml_cell_doc=celldoc,
        cd_id="pas",
        ion_channel="pas",
        cond_density=".0000975 S_per_cm2",
        erev="-70 mV",
        group_id="all",
        ion="non_specific",
        ion_chan_def_file="channels/pas.channel.nml",
    )
    cell.set_resistivity("35.4 ohm_cm", group_id="all")
    cell.set_specific_capacitance("1 uF_per_cm2", group_id="all")
    cell.set_init_memb_potential("-80mV")

    # L1 validation
    # cell.validate(recursive=True)
    cell.summary(morph=False, biophys=True)
    # use pynml writer to also run L2 validation
    write_neuroml2_file(celldoc, "KC.cell.nml")


def KC_create_na_channel():
    """Create the Na channel.

    This will create the Na channel and save it to a file.
    It will also validate this file.

    returns: name of the created file
    """
    na_channel = component_factory(
        "IonChannelHH",
        id="na_channel",
        notes="Sodium channel for HH cell",
        conductance="10pS",
        species="na",
        validate=False,
    )
    gate_m = component_factory(
        "GateHHRates",
        id="m",
        instances="3",
        notes="m gate for na channel",
        validate=False,
    )
    m_forward_rate = component_factory(
        "HHRate", type="HHExpLinearRate", rate="1per_ms", midpoint="-40mV", scale="10mV"
    )
    m_reverse_rate = component_factory(
        "HHRate", type="HHExpRate", rate="4per_ms", midpoint="-65mV", scale="-18mV"
    )

    gate_m.add(m_forward_rate, hint="forward_rate", validate=False)
    gate_m.add(m_reverse_rate, hint="reverse_rate")
    na_channel.add(gate_m)

    gate_h = component_factory(
        "GateHHRates",
        id="h",
        instances="1",
        notes="h gate for na channel",
        validate=False,
    )
    h_forward_rate = component_factory(
        "HHRate", type="HHExpRate", rate="0.07per_ms", midpoint="-65mV", scale="-20mV"
    )
    h_reverse_rate = component_factory(
        "HHRate", type="HHSigmoidRate", rate="1per_ms", midpoint="-35mV", scale="10mV"
    )
    gate_h.add(h_forward_rate, hint="forward_rate", validate=False)
    gate_h.add(h_reverse_rate, hint="reverse_rate")
    na_channel.add(gate_h)

    na_channel_doc = component_factory(
        "NeuroMLDocument", id="na_channel", notes="Na channel for HH neuron"
    )
    na_channel_fn = "HH_example_na_channel.nml"
    na_channel_doc.add(na_channel)
    na_channel_doc.validate(recursive=True)

    write_neuroml2_file(
        nml2_doc=na_channel_doc, nml2_file_name=na_channel_fn, validate=True
    )

    return na_channel_fn


if __name__ == "__main__":
    postprocess_GGN()
