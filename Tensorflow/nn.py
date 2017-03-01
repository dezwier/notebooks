import tensorflow as tf
import numpy as np


def plotter(history):
    at, av, lt, lv = zip(*history)
    fig = plt.figure(figsize=(15, 8)); ax1 = fig.add_subplot(221); ax2 = fig.add_subplot(222)

    ax1.plot(np.arange(0, len(at), 1), at,".-", color='#2A6EA6', label="Training: {0:.2f}%".format(at[-1]))
    ax1.plot(np.arange(0, len(av), 1), av,".-", color='#FFA933', label="Validation: {0:.2f}%".format(av[-1]))
    ax1.grid(True); ax1.legend(loc="lower right"); ax1.set_title("Accuracy per epoch")

    ax2.plot(np.arange(0, len(lt), 1), lt,".-", color='#2A6EA6', label="Training: {0:.2f}".format(lt[-1]))
    ax2.plot(np.arange(0, len(lv), 1), lv,".-", color='#FFA933', label="Validation: {0:.2f}".format(lv[-1]))
    ax2.grid(True); ax2.legend(loc="upper right"); ax2.set_title("Cost per epoch")
    plt.show()
    
def createNeuralNetwork(DATA, NEURONS, BATCH, RATE, STEPS, BREAKS):
    
    trainX = DATA[0]
    trainY = DATA[1]
    validX = DATA[2]
    validY = DATA[3]

    graph = tf.Graph()
    with graph.as_default():

        # Input data.
        tfDataX = tf.placeholder(tf.float32, shape=(None, NEURONS[0]))
        tfDataY = tf.placeholder(tf.float32, shape=(None, NEURONS[-1]))

        # Variables.
        w1 = tf.Variable(tf.truncated_normal([NEURONS[0], NEURONS[1]], stddev=np.sqrt(2.0/NEURONS[1])))
        b1 = tf.Variable(tf.zeros(NEURONS[1]))
        
        w2 = tf.Variable(tf.truncated_normal([NEURONS[1], NEURONS[2]], stddev=np.sqrt(2.0/NEURONS[2])))
        b2 = tf.Variable(tf.zeros(NEURONS[2]))

        wn = tf.Variable(tf.truncated_normal([NEURONS[-2], NEURONS[-1]], stddev=np.sqrt(2.0/NEURONS[-2])))
        bn = tf.Variable(tf.zeros(NEURONS[-1]))

        # Model.
        def model(x):
            x = tf.nn.relu(tf.matmul(x, w1) + b1)
            x = tf.nn.relu(tf.matmul(x, w2) + b2)
            x = tf.nn.relu(tf.matmul(x, wn) + bn)
            return x

        # Training computation.
        logits = model(tfDataX)
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=tfDataY))
        rate = tf.train.exponential_decay(RATE, tf.Variable(0), 4000, 0.65, staircase=True)
        optimizer = tf.train.GradientDescentOptimizer(rate).minimize(loss)

        # Predictions and Accuracy.
        predictions = {"classes": tf.argmax(model(tfDataX), axis=1), "probabilities": tf.nn.softmax(model(tfDataX))}
        accuracy = tf.reduce_mean(tf.to_float(tf.equal(predictions["classes"], tf.argmax(tfDataY, axis=1)))) * 100
        
        
    with tf.Session(graph=graph) as session:
        tf.global_variables_initializer().run()
        history = []
        for step in range(STEPS):
            offset = (step * BATCH) % (trainY.shape[0] - BATCH)
            batchX = trainX[offset:(offset + BATCH), :]
            batchY = trainY[offset:(offset + BATCH), :]
            session.run(optimizer, {tfDataX: trainX, tfDataY: trainY})
            if(step % (STEPS // BREAKS) == 0):
                lt, at = session.run([loss, accuracy], {tfDataX: trainX, tfDataY: trainY})
                lv, av = session.run([loss, accuracy], {tfDataX: validX, tfDataY: validY})
                history.append((at, av, lt, lv))
                print ".",
        predictions = session.run(predictions, {tfDataX: validX})
        #accuracy = session.run(accuracy, {tfDataX: testX, tfDataY: testY})
        #print('\nTest accuracy: %.2f%%' % accuracy)