"""
Created on Nov 3, 2013

@author: Nicklas Boerjesson
"""



from qal.common.resources import Resources
from qal.tools.transform import make_transformation_array_from_xml_node, make_transformations_xml_node, perform_transformations
from qal.tools.diff import compare
from qal.dataset.factory import dataset_from_resource
from qal.sql.macros import select_all_skeleton
from qal.dal.dal import Database_Abstraction_Layer
from lxml import etree


def isnone( _node):
    if _node == None or _node.text == None:
        return None
    else:
        return _node.text  
    
class Field_Mapping(object):
    is_key = None 
    src_column = None
    src_datatype = None
    src_cast_to = None
    result_cast_to = None
    dest_column = None
    transformations = []
    
    def __init__(self, _xml_node = None):
        """
        Constructor
        """
        if _xml_node != None:
            self.load_from_xml_node(_xml_node)
        else:
            raise Exception("Field_Mapping.load_from_xml_node: \"None\" is not a valid Merge node.")     
    
    def load_from_xml_node(self, _xml_node):
        if _xml_node != None:
            self.is_key = isnone(_xml_node.find("is_key"))
            self.src_column = isnone(_xml_node.find("src_column"))
            self.src_datatype = isnone(_xml_node.find("src_datatype"))
            self.src_cast_to = isnone(_xml_node.find("src_cast_to"))
            self.result_cast_to = isnone(_xml_node.find("result_cast_to"))
            self.dest_column = isnone(_xml_node.find("dest_column"))
            self.transformations = make_transformation_array_from_xml_node(_xml_node.find("transformations"))
         
            
    def as_xml_node(self):

        _xml_node = etree.Element("field_mapping")        
        etree.SubElement(_xml_node, "is_key").text = self.is_key
        etree.SubElement(_xml_node, "src_column").text = self.src_column
        etree.SubElement(_xml_node, "src_datatype").text = self.src_datatype
        etree.SubElement(_xml_node, "src_cast_to").text = self.src_cast_to
        _xml_node.append(make_transformations_xml_node(self.transformations))
        etree.SubElement(_xml_node, "result_cast_to").text = self.result_cast_to
        etree.SubElement(_xml_node, "dest_column").text = self.dest_column

        

        return _xml_node

class Merge(object):
    mappings = []
    key_fields = []
    source = None
    destination = None
    source_table = None
    destination_table = None
    resources = None
    destination_log_level = None
    
    """
    The merge class takes two datasets and merges them together.
    """


    def __init__(self, _xml_node = None):
        """
        Constructor
        """
        self.mappings = []
        self.key_fields = []
        if _xml_node != None:
            self.load_from_xml_node(_xml_node)
        else:
            raise Exception("Merge.load_from_xml_node: \"None\" is not a valid Merge node.")                  
    
    
    def _field_mappings_as_xml_node(self):
        _xml_node = etree.Element("field_mappings")
        for _curr_mapping in self.mappings:
            _xml_node.append(_curr_mapping.as_xml_node())
        
        return _xml_node    

    def _table_mappings_as_xml_node(self):
        _xml_node = etree.Element("table_mappings")
        etree.SubElement(_xml_node, "source_table").text = self.source_table
        etree.SubElement(_xml_node, "destination_table").text = self.destination_table
        
        return _xml_node    
    
    def _mappings_as_xml_node(self):
        _xml_node = etree.Element("mappings")
        _xml_node.append(self._field_mappings_as_xml_node())
        _xml_node.append(self._table_mappings_as_xml_node())
        return _xml_node
    
    def _settings_as_xml_node(self):
        _xml_node = etree.Element("settings")
        etree.SubElement(_xml_node, "insert").text = self.insert
        etree.SubElement(_xml_node, "update").text = self.update
        etree.SubElement(_xml_node, "delete").text = self.delete
        return _xml_node    
    
    
    def as_xml_node(self):
        _xml_node = etree.Element('merge')
        _xml_node.append(self._mappings_as_xml_node())
        _xml_node.append(self._settings_as_xml_node())
        _xml_node.append(self.resources.as_xml_node())
        return _xml_node        
        
    def load_field_mappings_from_xml_node(self, _xml_node):
        if _xml_node != None:
            _mapping_idx = 0
            for _curr_mapping in _xml_node.findall("field_mapping"):
                _new_mapping = Field_Mapping(_xml_node = _curr_mapping)
                self.mappings.append(_new_mapping)
                if _new_mapping.is_key == "True":
                    self.key_fields.append(_mapping_idx)  
                _mapping_idx+= 1              
        else:
            raise Exception("Merge.load_field_mappings_from_xml_node: Missing 'field_mappings'-node.")   

    def load_table_mappings_from_xml_node(self, _xml_node):
        if _xml_node != None:
            self.source_table = isnone(_xml_node.find("source_table"))
            self.destination_table = isnone(_xml_node.find("destination_table"))
        else:
            raise Exception("Merge.load_table_mappings_from_xml_node: Missing 'table_mappings'-node.")   

    def load_mappings_from_xml_node(self, _xml_node):
        if _xml_node != None:
            self.load_field_mappings_from_xml_node(_xml_node.find("field_mappings"))
            self.load_table_mappings_from_xml_node(_xml_node.find("table_mappings"))
        else:
            raise Exception("Merge.load_field_mappings_from_xml_node: Missing 'mappings'-node.")   
        

    def load_settings_from_xml_node(self, _xml_node):
        if _xml_node != None:
            self.insert = isnone(_xml_node.find("insert"))
            self.update = isnone(_xml_node.find("update"))
            self.delete = isnone(_xml_node.find("delete"))     
        else:
            raise Exception("Merge.load_settings_from_xml_node: Missing 'settings'-node.")     
               
    def load_from_xml_node(self, _xml_node):

        if _xml_node != None:           
            self.load_mappings_from_xml_node(_xml_node.find("mappings"))
            self.load_settings_from_xml_node(_xml_node.find("settings"))
            self.resources = Resources(_resources_node= _xml_node.find("resources"))
            
        else:
            raise Exception("Merge.load_from_xml_node: \"None\" is not a valid Merge node.")                  

   
    

    
    def _load_resources(self):
        
        # Load source_dataset
        self.source = dataset_from_resource(self.resources.get_resource('source_uuid'))
        self.source.table_name = self.source_table
        try:
            self.source.load()
        except Exception as e:
            raise Exception("Merge._load_resources: Failed loading data for source data set.\n" + \
                            "Resource: " + str(self.resources.get_resource('source_uuid').caption)+ "(" + str(self.resources.get_resource('source_uuid').uuid) + ")\n"+ \
                            "Error: " + str(e))
        
        # Load destination dataset
        self.destination = dataset_from_resource(self.resources.get_resource('dest_uuid'))
        self.destination.table_name = self.destination_table
        try:
            self.destination.load()
        except Exception as e:
            raise Exception("Merge._load_resources: Failed loading data for source data set.\n" + \
                            "Resource: " + str(self.resources.get_resource('dest_uuid').caption)+ "(" + str(self.resources.get_resource('dest_uuid').uuid) + ")\n"+ \
                            "Error: " + str(e))

       
        if self.destination_log_level:
            self.destination._log_level = self.destination_log_level
             
    def _make_shortcuts(self):
        """Make a list of which source column index maps to which destination column index""" 
        _shortcuts = []       

        # Make mapping
        for _curr_mapping in self.mappings:
            _src_idx  = self.source.field_names.index(_curr_mapping.src_column)
            _dest_idx = self.destination.field_names.index(_curr_mapping.dest_column)
            _shortcuts.append([_src_idx, _dest_idx, _curr_mapping])
            
        return _shortcuts
         

    def _remap_and_transform(self):
        """Create a remapped source data set that has the same data in the same columns as the destination data set.
        Also applies transformations."""
        _shortcuts = self._make_shortcuts()

        _mapped_source = []
        # Loop all rows in the source data set
        for _curr_idx in range(0, len(self.source.data_table)):
            # Create an empty row with None-values to fill later
            _curr_mapped = []
            _curr_mapped.extend(None for x in self.destination.field_names)
            
            _curr_row = self.source.data_table[_curr_idx]
            # Loop all the shortcuts to remap the data from the source structure into the destinations 
            # structure while applying transformations.
            for _curr_shortcut in _shortcuts:
                try:
                    _value = perform_transformations(_curr_row[_curr_shortcut[0]], _curr_shortcut[2].transformations)
                except Exception as e:
                    raise Exception("Merge._remap_and_transform:\nError in applying transformations for row " + 
                                    str(_curr_idx) + ", column \"" + self.destination.field_names[_curr_shortcut[0]] + 
                                    "\":\n" + str(e))
                # Set the correct field in the destination data set
                _curr_mapped[_curr_shortcut[1]] = _value
            _mapped_source.append(_curr_mapped)
        
        return _mapped_source
           
    def execute(self):
        
        # Load resources
        self._load_resources()
        
        # Create a remapped source dataset, perform transformations
        _mapped_source = self._remap_and_transform()
        

        """Merge the datasets"""
        _merged_dataset = self.destination.apply_new_data(_mapped_source, self.key_fields)

        self.destination.save()
        
        return _merged_dataset

        