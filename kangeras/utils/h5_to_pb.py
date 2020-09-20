# Author: Jason Dsouza
# Github: http://www.github.com/jasmcaus

import os
# Surpressing Tensorflow Warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
# 0 = all messages are logged (default behavior)
# 1 = INFO messages are not printed
# 2 = INFO and WARNING messages are not printed
# 3 = INFO, WARNING, and ERROR messages are not printed

# Importing the necessary packages
import tensorflow as tf

def h5_to_pb(model, base_name, DIR, session=None,learning_phase=None):
    """
        Converts a Keras .h5 model and converts to a Tensorflow '.pb' and '.pbtxt'model
        There are some variables which are being computed in training phase for future use.

        If you don't change to test phase, it will use current values.
        For example dropout and batch normalization.

        If you use it in training mode, then for mean and variance it will use current values,
        but in test time it will use moving_mean and moving_variance.
        :param learning_phase: 0 (testing) or 1 (training)

        To import in OpenCV:
            model = cv.dnn.readNetFromTensorflow('name.pb')
    """
    output_names = [ouput.op.name for output in model.outputs]
    if DIR is None:
        DIR = './'

    if session is None:
        session = tf.compat.v1.keras.backend.get_session()

    if learning_phase is not None:
        if learning_phase in [0,1]:
            session.set_learning_phase(learning_phase)
        else:
            raise ValueError('[ERROR] Learning Phase should either be 0 (Testing) or 1 (Training)', learning_phase)
    else:
        session.set_learning_phase(0) # 0 (Testing); 1 (Training)

    pbtxt = base_name + '.pbtxt'
    pb = base_name + '.pb'

    # Writing the Frozen Graph to a .pb file
    write_frozen_graph(model, session, base_name, DIR)

def write_frozen_graph(model, session, name, DIR=None):
    """
        Writes the frozen graph and converts to '.pb' and '.pbtxt'
        To import in OpenCV:
            model = cv.dnn.readNetFromTensorflow('name.pb')
    """
    # Creating the frozen graph
    frozen_graph = freeze_tf_session(model, session, output_names=output_names)
    # Writing the graph
    tf.train.write_graph(frozen_graph, DIR, pbtxt, as_text=True)
    tf.train.write_graph(frozen_graph, DIR, pb, as_text=False)

def freeze_tf_session(model, session, keep_var_names=None, output_names=None, clear_devices=True):
    """
    Freezes the state of a session into a pruned computation graph.

    Creates a new computation graph where variable nodes are replaced by
    constants taking their current value in the session. The new graph will be
    pruned so subgraphs that are not necessary to compute the requested
    outputs are removed.
    @param session The TensorFlow session to be frozen.
    @param keep_var_names A list of variable names that should not be frozen,
                          or None to freeze all the variables in the graph.
    @param output_names Names of the relevant graph outputs.
    @param clear_devices Remove the device directives from the graph for better portability.
    @return The frozen graph definition.
    """
    graph = session.graph
    with graph.as_default():
        freeze_var_names = list(set(var.op.name for var in tf.global_variables()).difference(keep_var_names or []))
        output_names = output_names or []
        output_names += [var.op.name for var in tf.global_variables()]
        input_graph_def = graph.as_graph_def()
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ''
        frozen_graph = tf.graph_util.convert_variables_to_constants(
            session, input_graph_def, output_names, freeze_var_names)
        return frozen_graph

def model_io(model, inputs=True, outputs=True):
    if inputs:
        model_inputs = [input.op.name for input in model.inputs]
        print('Model Inputs:')
        print(model_inputs)
    if outputs:
        model_outputs = [ouput.op.name for output in model.outputs]
        print('Model Outputs:')
        print(model_inputs)