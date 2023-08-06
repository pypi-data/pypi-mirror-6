from collections import OrderedDict as OD
from lxml import etree
from copy import deepcopy

class Metadata(object):
  """
  Generic class to hold metadata nodes. Nodes can be added by simply calling Metadata.add_node(node_object)
  Alternatively nodes can be input with a file parser.

  Attributes
  ----------
  fname: string
    The path and name of a flat file that is going to be parsed
  root: int
    The root node of the xml tree, this is set automatically by the file parser, but must be set manually for all other types of object creation
  etree_nodes: OrderedDict
    A dictionary of exported nodes.  After nodes have been exported into etree elements they are stored here.  They can be accessed by UID key.
  nodes: Dictionary
    A dictionary of all the nodes, all of which are of class MD_node, and can be accessed by UID key.
  tree: lxml etree
    The xml etree of the entire Metadata object
  tree_struct: Dictionary
    Holds the tree structure as a dictionary in the form {Parent_node: [child_node1, child_node2...child_noden]}
  """

  def __init__(self, fname = ""):

    # The file name to parse when we get there
    self.fname = fname
    # the root node ID
    self.root = 0
    #  Holds exported nodes as individual etree elements
    self.etree_nodes = OD()
    # Dictionary of nodes referenced by UID
    self.nodes = {}
    if fname:
      self.ingest()

    # Holds the etree from parsed input
    self.tree = None
    # Holds tree strucure
    self.tree_struct = {}




  def add_node(self,MD_node):
    """
    Just adds a node to the dictionary
    """
    self.nodes[MD_node.UID] = MD_node


  def ingest(self):
     """
     Parse a flat file into a metadata object.  Takes a file specified by the creation of the metadata object and populates nodes.  Format is as follows.
     The following three headers are a requirement and must be specified in order:

     Parent_ID: <ID or None for root node>

     Node_ID: <ID for the node>

     Node_Name: <Name of the node>

     The remaining entries are free form and specified as:

     <element> : <value>

     If a given element has attributes they can be specified with a "-'' character

     <element> : <value> -- <attribute name> : <attribute value> -- <attribute name> : <attribute value> etc...

     """
     node_header = OD()
     node_data = []
     # Keep track of the starting node
     ncount = 0
     nodedict = OD()
     f = open(self.fname,"r")
     for lines in f:
          # Split the string into components
          # Run through some if statements to capture headers
          spltstr = lines.split(":",1)
          ## clean up the string
          spltstr = map(lambda x: x.rstrip().strip(),spltstr)
          if "Parent_ID" in spltstr[0]:
            if ncount > 0:
                    ### Create a new node
              new_node = MD_node(node_header["Node_ID"], name = node_header["Node_Name"], parent = node_header["Parent_ID"],  data = node_data , node_attr=node_header["Node_attrib"])
              nodedict[int(node_header["Node_ID"])] = new_node
               ### Reset data if a new parent id is encountered, denoting a new node
            node_header = OD()
            node_data = []
            ncount += 1
               ### Capture the none case
            try:
              node_header["Parent_ID"] = int(spltstr[1])
            except ValueError:
              node_header["Parent_ID"] = spltstr[1]



          elif "Node_ID" in spltstr[0]:

            node_header["Node_ID"] = int(spltstr[1])
            if node_header["Parent_ID"] == "None" or node_header["Parent_ID"] == "none":
              node_root = int(spltstr[1])


          elif "Node_Name" in spltstr[0]:
            ### Automatically root the xml tree

            node_header["Node_Name"] = spltstr[1].rstrip().strip()
            if "--" in spltstr[1]:
              subsplt = spltstr[1].split("--")
              node_header["Node_Name"] = subsplt[0].rstrip().strip()
              attr_dict = OD()
              for j in subsplt[1:]:
                asplit = j.split(":",1)
                stext = map(lambda x: x.rstrip().strip(),asplit)
                attr_dict[stext[0]] = stext[1]
              node_header["Node_attrib"] = attr_dict
            else:
              node_header["Node_attrib"] = OD()

          elif len(spltstr) > 1:
               ### Create temporary element
               tmp_el = MD_element()
               ### Check for attributes
               if "--" in spltstr[1]:
                    attr_dict = OD()
                    subsplt = spltstr[1].split("--")
                    tmp_el.tag = spltstr[0]
                    tmp_el.text = subsplt[0]
                    for j in subsplt[1:]:
                         asplit = j.split(":",1)
                         asplit = map(lambda x: x.rstrip().strip(),asplit)
                         attr_dict[asplit[0]]= asplit[1]

                    tmp_el.attr = attr_dict
                    node_data.append(tmp_el)
               else:
                    tmp_el.tag = spltstr[0]
                    tmp_el.text = spltstr[1]
                    node_data.append(tmp_el)
     f.close()
     ### Write the last node
     new_node = MD_node(node_header["Node_ID"], name = node_header["Node_Name"], parent = node_header["Parent_ID"],  data = node_data ,  node_attr=node_header["Node_attrib"])
     nodedict[int(node_header["Node_ID"])] =new_node

     self.nodes = nodedict
     self.root = node_root





  def create_tree(self):
    """
      Creates a dictionary of nodes.  Nodes are added arbitrarily to a dictionary, without structure.  This will create a parent child type structure and store it in self.tree_struct

    """
    ## Loop through node dictionary and create tree.

    for k,v in self.nodes.iteritems():

     ## Get parent UID's
    ## Lot's of ints and strings to convert between types for proper comparisons
      pid = v.parent
      if any(pid == j for j in self.tree_struct.keys()) and not any(k == j for j in self.tree_struct[pid]) and v.UID != self.root:
        self.tree_struct[pid].append(k)
      elif pid and v.UID != self.root:
        self.tree_struct[pid] = [k]



  def traverse(self):
    r"""
      Traverse the metadata tree in a depth first post order.

    """
    pstack = [0]
    cnode = self.root
    ### Get list of all nodes to ensure I visit them all.
    ## make copy of the tree structure you can prune
    node_dict = deepcopy(self.tree_struct)
    nodes_list = self.list_from_vals(node_dict)

    ### Loop over all nodes
    while nodes_list:
      #check if a node has children
      childs = self.has_child(cnode,node_dict)
      if childs:
        # If it does then the current
        parent = cnode
        cnode = childs[0]
        if parent not in pstack:
          pstack.append(parent)
      else:
        ## Remove from the master list
        nodes_list.remove(cnode)
        ### Remove from the dictionary
        node_dict[pstack[-1]].remove(cnode)
        self.export_node(cnode)
        ### check if the parent stack needs to adjusted.
        ### if so pop off value
        if not node_dict[pstack[-1]]:
          pstack.pop()
        cnode = pstack[-1]
    ### Adjust for exporting root
    self.export_node(self.root)



  def has_child(self, nuid, node_dict):
    r"""
    Determine if a given node ID has children, used in tree traversal

    Parameters
    ---------------
    nuid:
      The uid (within the metadata structure) to check if it has any children

    nodes_dict: dict
      The dictionary containing the metadata tree structure

    Returns
    ---------
     list
      A list of child nodes for a given parent node

    """
    if any(nuid == k for k in node_dict.keys()):
      if isinstance(node_dict[nuid],int):
        return([node_dict[nuid]])
      else:
        return(node_dict[nuid])
    else:
      return(False)


  def list_from_vals(self,d):
    '''
    Flatten a list.
    '''
    out = []
    for i in d.values():
      for j in i:
        out.append(j)

    return(out)

  def export_node(self,nuid):
    """
    Export a given node as an ordered dictionary, in a format readable to the Metadata class

    Parameters
    -------------
    nuid: int
      The node ID to export

    Modifies
    --------
    self.etree_nodes
      adds exported node to the dictionary of etree nodes, with node ID as the dictionary key

    """
    nroot = etree.Element(self.nodes[nuid].name)
    for k in self.nodes[nuid].data:

        etree.SubElement(nroot,k.tag,attrib = k.attr).text=k.text



    ### Add attributes to root node
    for k,v in self.nodes[nuid].node_attr.iteritems():
      nroot.set(k,v)


    ### add in child nodes
    for k in self.tree_struct.keys():
      if(k == nuid):
        for j in self.tree_struct[nuid]:
          nroot.append(self.etree_nodes[j])
      #for j in self.tree_struct[nuid].values():
        #print j


    self.etree_nodes[nuid] = nroot

  def create_xml(self):
      '''
        Create an xml etree that can be print out.

        Modifies
        ----------
        self.tree
          Creates a full tree as an etree object, can be used for printing and writing purposes.
      '''
      self.traverse()
      self.tree = self.etree_nodes[self.root]

  def print_xml(self):
    '''
      Pretty print Metadata object, just calles lxml pretty print method.  If you want more fancy print methods, use the etree.tostring method on Metadata.tree
    '''
    print(etree.tostring(self.tree,encoding="UTF-8",pretty_print=True,xml_declaration=True))




class MD_node(object):
  """

  A node class that contains all the data about that node.  A node is a top level xml container tag, which may contain child xml nodes.

  Attributes
  -----------------
  UID: int
    The unique identifier of a node
  name: string
    The name of a node
  parent: int
    The UID of a parent node
  data: list
    A list of data elements, must be of type MD_element
  node_attr: OrderedDict
    A dictionary of node attributes in

  """

  def __init__(self,UID, name, parent = None, data = [], node_attr = OD()):

    self.UID = UID
    self.name = name
    self.parent = parent
    self.data = data
    self.node_attr = node_attr


class MD_element(object):
  """
  Simple container for elements of a node.

  Attributes
  ------------
  tag: str
    The name of the XML element e.g. foo for the xml tag <foo>
  text: str
    The text value of the element, e.g. bar for the text in <foo> bar </foo>
  attr: OrderedDict
    A dictionary of attributes where keys are attributes and values are attribute values
  """

  def __init__(self, tag = "", text = "" , attr = OD()):
    self.tag = tag
    self.text = text
    self.attr = attr




