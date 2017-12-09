


# houdini tool
# Converts primGroups to Object Nodes
# create new tool on the tool shelf inside houdini. Choose "Edit tool" and copypaste this code

import hou

root_node_name = "groups_as_objects_from_"

path_to_source_geometry = ""

sop_nodes = []

for n in hou.session.hou.selectedNodes():
    if isinstance(n, hou.SopNode):
        sop_nodes.append(n)


try:
    path_to_source_geometry = sop_nodes[0].path()
except:
    pass

if not path_to_source_geometry:
    hou.ui.displayMessage("There's no any SOP nodes selected. Please select one.")


if path_to_source_geometry:
    prim_groups_count = len( hou.node(path_to_source_geometry).geometry().primGroups() )
    root_node_name += sop_nodes[0].name()

if path_to_source_geometry and prim_groups_count == 0:
    hou.ui.displayMessage("There's no any primitive groups. Please set at least one.")


if path_to_source_geometry and prim_groups_count > 0:

    prim_groups = hou.node(path_to_source_geometry).geometry().primGroups()

    groups_names = [ g.name() for g in prim_groups]


        
    #delete root node if already exists (need for correct updating)
    temp_ = hou.node("/obj").node(root_node_name)
    if temp_:
        temp_.destroy()

    #create root subnet node
    root = hou.node("/obj").createNode("subnet", node_name=root_node_name)
    str_parm = hou.StringParmTemplate("source_path", "Source Path", 1)
    # button_parm = hou.ButtonParmTemplate("update", "Update (Not Implemented)")


    # parm_folder = root.addSpareParmFolder("SOPs Groups")
    root.addSpareParmTuple(str_parm, in_folder=("Groups Source",), create_missing_folders=True) 
    # root.addSpareParmTuple(button_parm, in_folder=("Groups Source",), create_missing_folders=True)

    root.parm("source_path").set(path_to_source_geometry)


    for c, group_name in enumerate(groups_names):

        #create a representative for each group
        obj_geo = root.createNode("geo", node_name=group_name)



        obj_geo.move(hou.Vector2( (c % 3) * 3 , - (c // 3) ))
        
        #obj_geo.moveToGoodPosition()
        
        #delete auto-created node
        obj_geo.node("file1").destroy()


        #create node that we want to create inside
        sop_objmerge = obj_geo.createNode("object_merge", node_name=group_name)

        #change parameter to change
        sop_objmerge.parm("objpath1").set( path_to_source_geometry )
        sop_objmerge.parm("group1").set( group_name ) 


    msg = "%s obj-nodes has been created. Jump to the subnet?" % (c+1)
    if hou.ui.displayMessage(msg, buttons=("Yes", "No")) == 0:
        editors = [pane for pane in hou.ui.paneTabs() if isinstance(pane, hou.NetworkEditor) and pane.isCurrentTab()]
        editor = editors[0]
        editor.setPwd(root)
