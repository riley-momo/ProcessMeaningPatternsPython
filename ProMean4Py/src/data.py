# Process mining
import pm4py

# Data science
import numpy as np
import pandas as pd

# General / IO
import re
from string import Template
import tempfile
from itertools import combinations

# Knowledge graph / reasoning
import yatter
from ruamel.yaml import YAML
import kglab
import rdflib

class LogProcessor:
    def __init__(self, log_path,
                 column_dict={'case_id': 'case:concept:name', 'activity': 'concept:name', 'timestamp': 'time:timestamp', 'resource': 'org:resource', 'event_id' : None},
                 prefixes={'ex':'http://www.example.com/', 'on': 'https://stl.mie.utoronto.ca/ontologies/spm/'},
                 process_name='P1',
                 downsample_rate=1):
        self.process_name = process_name
        self.column_dict = column_dict
        self.prefixes = prefixes
        self.log_path = log_path
        self.downsample_rate = downsample_rate
        self.log_df = self.load_df_from_log()
        self.mapping = self.build_mapping()
        self.fol_abox = np.array([])

    
    def load_df_from_log(self):
        """
        Return a dataframe from a given XES log filepath or CSV 
        and creates a temporary csv file with additional columns needed for consistent processing.
        Optionally downsample data for large datasets (necessary for large logs to be used with first order logic reasoning at this stage)
        """
        log_path = self.log_path
        col_dict = self.column_dict
        if any(log_path.lower().endswith(ext) for ext in ['.xes', '.xes.gz']): # if log is in XES format
            log = pm4py.read_xes(log_path)
            df = pm4py.convert_to_dataframe(log)
            #df.to_csv(re.sub(r'\.xes(\.gz)?$', '.csv', log_path), index=False)
        elif log_path.lower().endswith('.csv'): # if log is in CSV format
            df = pd.read_csv(log_path)
        else: # if log is in an unsupported format
            return None

        # add a process instance column to the dataframe
        df['processID'] = self.process_name
        
        # ensure non-overlapping URIs by prefixing columns with letter type encoding
        if not col_dict['event_id']: # if no unique identifier for events, create one
            df['eventID'] = df.index
            self.column_dict['event_id'] = 'eventID'
            col_dict = self.column_dict
        df[col_dict['event_id']] = df[col_dict['event_id']].apply(lambda x: f'E_{str(x)}')
        df[col_dict['case_id']] = df[col_dict['case_id']].apply(lambda x: f'C_{str(x)}')
        df[col_dict['activity']] = df[col_dict['activity']].apply(lambda x: f'A_{str(x)}')
        df[col_dict['resource']] = df[col_dict['resource']].apply(lambda x: f'R_{str(x)}')
        
        # Normalize column names to avoid issues with special characters in mapping
        df.rename(columns={col_dict['case_id']: 'caseID', col_dict['activity'] : 'activityID', col_dict['resource']: 'resourceID', col_dict['timestamp']: 'timestamp'}, inplace=True)
        # Also rename values in the column dictionary to reflect changes
        self.column_dict = {'case_id': 'caseID', 'activity': 'activityID', 'timestamp': 'timestamp', 'resource': 'resourceID', 'event_id' : 'eventID'}
        
        # downsample data if necessary
        if self.downsample_rate < 1:
            # sample by caseID
            unique_cases = df['caseID'].unique()
            sampled_cases = np.random.choice(unique_cases, int(self.downsample_rate * len(unique_cases)), replace=False)
            df = df[df['caseID'].isin(sampled_cases)]
        
        # create temporary log csv
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(df.to_csv(index=False))
            self.log_path = f.name
        
        return df
    
    def build_mapping(self):
        """
        Modifies YARRML mapping according to expected columns in the log
        """
        
        mapping_template = """
        prefixes:
            ex: $ex_prefix
            on: $on_prefix

        mappings:
            events:
                sources:
                - ['$log_path~$log_format']
                s: ex:$$($eventID)
                po:
                - [a, on:Event]
                - [on:hasCase, ex:$$($caseID)]
                - [on:hasActivity, ex:$$($activityID)]
                - [on:hasResource, ex:$$($resourceID)]
                - [on:hasRecordedTime, $$($timestamp), xsd:dateTimeStamp]

            resources:
                sources:
                - ['$log_path~$log_format']
                s: ex:$$($resourceID)
                po:
                - [a, on:Resource]

            cases:
                sources:
                - ['$log_path~$log_format']
                s: ex:$$($caseID)
                po:
                - [a, on:Case]
                - [on:hasProcess, ex:$$(processID)]

            activities:
                sources:
                - ['$log_path~$log_format']
                s: ex:$$($activityID)
                po:
                - [a, on:Activity]
        """
        mapping_template = Template(mapping_template)
        mapping_string = mapping_template.substitute(
            log_path=self.log_path,
            log_format='csv',
            ex_prefix=self.prefixes['ex'],
            on_prefix=self.prefixes['on'],
            eventID=self.column_dict['event_id'],
            caseID=self.column_dict['case_id'],
            activityID=self.column_dict['activity'],
            resourceID=self.column_dict['resource'],
            timestamp=self.column_dict['timestamp']
        )
        yaml = YAML(typ='safe', pure=True)
        yarrrml_content = yaml.load(mapping_string)
        rml_mapping = yatter.translate(yarrrml_content)
        # write rml mapping to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ttl') as f:
            f.write(rml_mapping)
            self.rml_path = f.name
        
        return rml_mapping
    
    def generate_knowledge_graph(self, assume_distinct=False):
        """
        Generates a knowledge graph from the log and mapping
        """
        # init knowledge graph
        print("Generating knowledge graph...")
        kg = kglab.KnowledgeGraph(name="test", namespaces=self.prefixes)
        # generate config
        config_string = f"""
        [{self.process_name}]
        mappings={self.rml_path}
        """
        # write config to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write(config_string)
            kg_config_path = f.name
        # generate the knowledge graph from the config
        kg.materialize(kg_config_path)
        
        
        if assume_distinct:
            print("Adding disjointness axioms...")
            # add disjointness axioms to each individual
            i_c = kg.query_as_df(sparql="SELECT ?s ?o WHERE {?s ?p ?o . FILTER (?p = rdf:type)}")
            for c in i_c['o'].unique():
                # make individuals distinct within each class
                inds = i_c[i_c['o'] == c]['s'].values
                # sanitize strings by stripping <> characters
                inds = [ind.strip('<>') for ind in inds]
                # convert individuals to URIRefs
                inds = [rdflib.URIRef(ind) for ind in inds] 
                # iterate over unique individuals combinations
                for pair in combinations(inds, 2):
                    # add disjoint predicate to individuals
                    kg.add(pair[0], rdflib.URIRef("http://www.w3.org/2002/07/owl#differentFrom"), pair[1])
            
        self.kg = kg
        print("Knowledge graph generated.")
        
        return kg
        
    def save_knowledge_graph(self, output_path=None, format='ttl'):
        # if kg does not yet exist, first generate it
        if not hasattr(self, 'kg'):
            self.generate_knowledge_graph()
        # save to path if specified    
        if output_path:
            output_file = output_path + f'{self.process_name}_log_instances.{format}'
            self.kg.save_rdf(output_file, format=format)
        
        print("Knowledge graph saved.")
        
        return None
        
    def generate_FOL(self):
        """
        Generates a First Order Logic representation of the log
        """
        print("Generating First Order Logic representation...")
        
        if not hasattr(self, 'kg'):
            self.generate_knowledge_graph()
            
        # helper functions definitions for converting RDF to FOL    
        def query_and_apply(query, func):
            df = self.kg.query_as_df(sparql=query)
            vals = df.apply(func, axis=1).values
            self.fol_abox = np.concatenate((self.fol_abox, vals), axis=0)

        # define helper functions to strip URIs
        strip_ex_prefix  = lambda x: re.sub(r".*/|>$", '', x)
        strip_on_prefix = lambda x: re.sub(r".*:", '', x)
        # define helper functions for converting RDF literals to FOL
        unary_pred = lambda s,o : f'{strip_on_prefix(o)}({strip_ex_prefix(s)})'
        binary_pred = lambda s,p,o : f'{strip_on_prefix(p)}({strip_ex_prefix(s)}, {strip_ex_prefix(o)})'
        
        # helper function for converting timepoints from data property to FOL
        def convert_timepoints(kg):
            tp_query = "SELECT ?s ?t WHERE {?s ns1:hasRecordedTime ?t}"
            df = kg.query_as_df(sparql=tp_query)
            unique_timestamps = df['t'].unique()
            # create timestamp mapping
            timestamp_mapping = {timestamp: f'ts_{i}' for i, timestamp in enumerate(sorted(unique_timestamps))}
            # apply mapping
            df['new_t'] = df['t'].map(timestamp_mapping)
            # create ordering relations over timestamps
            unique_mapped_timestamps = sorted(df['new_t'].unique())
            timestamp_pairs = [(unique_mapped_timestamps[i], unique_mapped_timestamps[i+1]) for i in range(len(unique_mapped_timestamps) - 1)]
            before_relations = [f'before({t1},{t2})' for t1, t2 in timestamp_pairs]
            timestamp_preds = [f'timepoint({t})' for t in unique_mapped_timestamps]
            event_timings = df.apply(lambda x: 'hasRecordedTime({}, {})'.format(re.sub(r".*/|>$", '', x["s"]), x["new_t"]), axis=1).values
            # add to Abox
            self.fol_abox = np.concatenate((self.fol_abox, timestamp_preds, event_timings, before_relations), axis=0)
        
        
        # Convert simple unary rdf:type predicates
        type_query = "SELECT ?s ?o WHERE {?s a ?o}"
        type_f = lambda x: unary_pred(x['s'], x['o'])
        query_and_apply(type_query, type_f)
        
        # convert binary relations other than time and rdf:type
        relation_query = "SELECT ?s ?p ?o WHERE {?s ?p ?o . FILTER (?p != rdf:type && ?p != ns1:hasRecordedTime)}"
        relation_f = lambda x: binary_pred(x['s'], x['p'], x['o'])
        query_and_apply(relation_query, relation_f)
        
        # convert timepoints
        convert_timepoints(self.kg)
        
        print("First Order Logic representation generated.")
        
        return self.fol_abox
        
    def save_FOL(self, output_dir=None, format='prover9'):
        
        if self.fol_abox.size == 0:
            self.generate_FOL()
            
        if output_dir:
            file_ext_map = {'prover9': '.p9', 'clif': '.clif'}
            literal_map = {'prover9': lambda x: f'{str(x)}.\n', 'clif': lambda x: f'({str(x)}\n)'}
            output_file = output_dir + f'{self.process_name}_log_literals{file_ext_map[format]}'
        
            with open(output_file, 'w') as f:
                for item in self.fol_abox:
                    f.write(literal_map[format](item))
                    
        print("First Order Logic literals saved.")
        
        return None
    
    def save_datalog(self, output_dir=None):
        
        # datalog facts are just a syntactic difference from FOL literals
        if self.fol_abox.size == 0:
            self.generate_FOL()
        
        # start with copy of FOL literals
        dl_facts = np.array([f'{str(x)}.' for x in self.fol_abox])
        # replace camel case with underscores
        dl_facts = np.array([re.sub(r'(?<!^)(?=[A-Z])(?=.*\()', '_', x) for x in dl_facts])
        # make sure predicates are lowercase
        dl_facts = np.array([x.lower() for x in dl_facts])
        # eliminate special characters
        dl_facts = np.array([re.sub(r'[<>\-%!#$^&*]', '', x) for x in dl_facts])
        
        self.dl_facts = dl_facts
        
        # generate output file
        if output_dir:
            output_file = output_dir + f'{self.process_name}_log_facts.pl'
            with open(output_file, 'w') as f:
                for item in dl_facts:
                    f.write(f'{item}\n')