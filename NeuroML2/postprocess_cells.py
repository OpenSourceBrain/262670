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

    cell.add_channel_density(
        nml_cell_doc=celldoc,
        cd_id="nas",
        ion_channel="nas",
        cond_density="3e-3 S_per_cm2",
        erev="-58 mV",
        group_id="all",
        ion="na",
        ion_chan_def_file="channels/nas.channel.nml",
    )
    cell.add_channel_density(
        nml_cell_doc=celldoc,
        cd_id="naf",
        ion_channel="naf",
        cond_density="3.5e-2 S_per_cm2",
        erev="-58 mV",
        group_id="all",
        ion="na",
        ion_chan_def_file="channels/naf.channel.nml",
    )
    cell.add_channel_density(
        nml_cell_doc=celldoc,
        cd_id="kv",
        ion_channel="kv",
        cond_density="1.5e-3 S_per_cm2",
        erev="-81 mV",
        group_id="all",
        ion="k",
        ion_chan_def_file="channels/kv.channel.nml",
    )
    cell.add_channel_density(
        nml_cell_doc=celldoc,
        cd_id="ka",
        ion_channel="ka",
        cond_density="1.4525e-2 S_per_cm2",
        erev="-81 mV",
        group_id="all",
        ion="k",
        ion_chan_def_file="channels/ka.channel.nml",
    )
    cell.add_channel_density(
        nml_cell_doc=celldoc,
        cd_id="kst",
        ion_channel="kst",
        cond_density="2.0275e-3 S_per_cm2",
        erev="-81 mV",
        group_id="all",
        ion="k",
        ion_chan_def_file="channels/kst.channel.nml",
    )

    # L1 validation
    # cell.validate(recursive=True)
    cell.summary(morph=False, biophys=True)
    # use pynml writer to also run L2 validation
    write_neuroml2_file(celldoc, "KC.cell.nml")


if __name__ == "__main__":
    postprocess_GGN()
    postprocess_KC()
