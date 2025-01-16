# Process Meaning Patterns - Python Repository

Process Meaning Patterns is a framework designed to enable ontology-aware process mining. Ontology-aware process mining is meant to formalize process knowledge applied throughout the process mining lifecycle to enable transparency and replicability. This is accomplished through *process meaning patterns*, first-order logic ontology patterns that correspond to common verification and inference steps in the process mining lifecycle. This repository contains an implementation of the process meaning pattern framework implemented in python and supporting exporting of process knowledge to various formats including OWL/RDF, First order logic via CLIF or Prover9 syntax, and prolog/datalog. 

The process meaning patterns framework is actively maintaned and developed by [Riley Moher](https://riley-momo.github.io/) of the semantic technologies (stl) laboratory at the University of Toronto.

## Example Usage

The central object of the process meaning pattern library is the LogProcessor, which can ingest a business process event log in a variety of formats and output corresponding facts to be validated against or queried with process meaning patterns. Here is a simple example:

```python
import ProMean4Py

# define column names
col_dict = {'case_id': 'caseID', 'activity': 'activityID', 'timestamp': 'timestamp', 'resource': 'resourceID', 'event_id' : 'eventID'}
# create output directory
output_dir= '../output/testing/'
# define namespaces for knowledge graph
namespaces = {'ex' : "http://example.com/", 'on' : "https://stl.mie.utoronto.ca/ontologies/spm/"}
# initialize the log processor on some data
log_processor = LogProcessor('sample_log.csv', process_name='P1', column_dict=col_dict, prefixes=namespaces)
# save the event log facts as a knowledge graph
log_processor.save_knowledge_graph(output_dir, format='xml')
# save the event log facts as first-order-logic facts
log_processor.save_FOL(output_dir)
# save the event log facts as datalog facts
log_processor.save_datalog(output_dir)

```


More thorough examples, including an example utilizing real-world enterprise data, are available in the notebooks directory of this repository.


## Installation

ProMean4Py is published on the python package index (pypi) and can be installed on any python version >= 3.9.X by simply invoking pip:

`pip install ProMean4Py`

## Release Notes

Release notes are tracked in the CHANGELOG.md file of this repository.
