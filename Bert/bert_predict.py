import torch
import time
import random
import datetime
import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import BertTokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertForSequenceClassification, AdamW, BertConfig
from transformers import get_linear_schedule_with_warmup
from sklearn.model_selection import StratifiedKFold, KFold
import argparse
from sklearn.metrics import f1_score, precision_score, recall_score




def check_for_gpu():
    # Get the GPU device name.
    device_name = tf.test.gpu_device_name()
    # The device name should look like the following:
    if device_name == '/device:GPU:0':
        print('Found GPU at: {}'.format(device_name))
    else:
        raise SystemError('GPU device not found')

def initiate_bert():
    # identify and specify the GPU as the device
    # If there's a GPU available...
    if torch.cuda.is_available():

        # Tell PyTorch to use the GPU.
        device = torch.device("cuda")

        print('There are %d GPU(s) available.' % torch.cuda.device_count())

        print('We will use the GPU:', torch.cuda.get_device_name(0))

    # If not...
    else:
        print('No GPU available, using the CPU instead.')
        device = torch.device("cpu")
    return device


def initiate_data(file):
    dataset = pd.read_csv(file)

    # Report the number of sentences.
    print('Number of training sentences: {:,}\n'.format(dataset.shape[0]))

    # Display 10 random rows from the data.
    # print(dataset.sample(10))

    # Get the lists of sentences and their labels.
    sentences = dataset.text.values

    # -------------------------------------------------------------------

    # Load the BERT tokenizer.
    print('Loading BERT tokenizer...')
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)

    # Tokenize all of the sentences and map the tokens to thier word IDs.
    input_ids = []

    # For every sentence...
    for sent in sentences:
        # `encode` will:
        #   (1) Tokenize the sentence.
        #   (2) Prepend the `[CLS]` token to the start.
        #   (3) Append the `[SEP]` token to the end.
        #   (4) Map tokens to their IDs.
        encoded_sent = tokenizer.encode(
            sent,  # Sentence to encode.
            add_special_tokens=True,  # Add '[CLS]' and '[SEP]'

            # This function also supports truncation and conversion
            # to pytorch tensors, but we need to do padding, so we
            # can't use these features :( .
            # max_length = 128,          # Truncate all sentences.
            # return_tensors = 'pt',     # Return pytorch tensors.
        )

        # Add the encoded sentence to the list.
        input_ids.append(encoded_sent)

    # Print sentence 0, now as a list of IDs.
    # print('Original: ', sentences[0])
    # print('Token IDs:', input_ids[0])

    # -------------------------------------------------------------------

    print('Max sentence length: ', max([len(sen) for sen in input_ids]))

    # -------------------------------------------------------------------

    # We'll borrow the `pad_sequences` utility function to do this.

    # Set the maximum sequence length.
    # I've chosen 64 somewhat arbitrarily. It's slightly larger than the
    # maximum training sentence length of 47...
    MAX_LEN = 100

    print('\nPadding/truncating all sentences to %d values...' % MAX_LEN)

    print('\nPadding token: "{:}", ID: {:}'.format(tokenizer.pad_token, tokenizer.pad_token_id))

    # Pad our input tokens with value 0.
    # "post" indicates that we want to pad and truncate at the end of the sequence,
    # as opposed to the beginning.
    input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long",
                              value=0, truncating="post", padding="post")

    print('\nDone.')

    # -------------------------------------------------------------------

    # Create attention masks
    attention_masks = []

    # For each sentence...
    for sent in input_ids:
        # Create the attention mask.
        #   - If a token ID is 0, then it's padding, set the mask to 0.
        #   - If a token ID is > 0, then it's a real token, set the mask to 1.
        att_mask = [int(token_id > 0) for token_id in sent]

        # Store the attention mask for this sentence.
        attention_masks.append(att_mask)

    return input_ids, attention_masks, dataset


def train_predict(input_ids, attention_masks, pred_labels, dataset, FILE, device,
                  pred_input_ids, pred_attention_mask, pred_dataset):
    # -------------------------------------------------------------------

    # Use train_test_split to split our data into train and validation sets for
    # training
    for LABEL in pred_labels:

        print("working on", LABEL, "\n")
        labels = dataset[LABEL].values


        # -------------------------------------------------------------------

        # Convert all inputs and labels into torch tensors, the required datatype
        # for our model.
        train_inputs = torch.tensor(input_ids)
        prediction_inputs = torch.tensor(pred_input_ids)

        train_labels = torch.tensor(labels)

        train_masks = torch.tensor(attention_masks)
        prediction_masks = torch.tensor(pred_attention_mask)

        # -------------------------------------------------------------------

        # This section is basically aiming to save runtime memory using torch DataLoader class :)

        # The DataLoader needs to know our batch size for training, so we specify it
        # here.
        # For fine-tuning BERT on a specific task, the authors recommend a batch size of
        # 16 or 32.

        batch_size = 32

        # Create the DataLoader for our training set.
        train_data = TensorDataset(train_inputs, train_masks, train_labels)
        train_sampler = RandomSampler(train_data)
        train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

        # Create the DataLoader for our validation set.
        prediction_data = TensorDataset(prediction_inputs, prediction_masks)
        prediction_sampler = SequentialSampler(prediction_data)
        prediction_dataloader = DataLoader(prediction_data, sampler=prediction_sampler, batch_size=batch_size)

        # -------------------------------------------------------------------

        # Load BertForSequenceClassification, the pretrained BERT model with a single
        # linear classification layer on top.
        model = BertForSequenceClassification.from_pretrained(
            "bert-base-uncased",  # Use the 12-layer BERT model, with an uncased vocab.
            num_labels=6,  # The number of output labels--2 for binary classification.

            # You can increase this for multi-class tasks.
            output_attentions=False,  # Whether the model returns attentions weights.
            output_hidden_states=False,  # Whether the model returns all hidden-states.
        )

        # Tell pytorch to run this model on the GPU.
        model.cuda()

        # -------------------------------------------------------------------

        # Get all of the model's parameters as a list of tuples.
        params = list(model.named_parameters())

        """
        For the purposes of fine-tuning, the authors recommend choosing from the following values:

            Batch size: 16, 32 (We chose 32 when creating our DataLoaders).
            Learning rate (Adam): 5e-5, 3e-5, 2e-5 (We'll use 2e-5).
            Number of epochs: 2, 3, 4 (We'll use 4).

        """

        # Note: AdamW is a class from the huggingface library (as opposed to pytorch)
        # I believe the 'W' stands for 'Weight Decay fix"
        optimizer = AdamW(model.parameters(),
                          lr=2e-5,  # args.learning_rate - default is 5e-5, our notebook had 2e-5
                          eps=1e-8  # args.adam_epsilon  - default is 1e-8.
                          )

        # Number of training epochs (authors recommend between 2 and 4)
        epochs = 2

        # Total number of training steps is number of batches * number of epochs.
        total_steps = len(train_dataloader) * epochs

        # Create the learning rate scheduler.
        scheduler = get_linear_schedule_with_warmup(optimizer,
                                                    num_warmup_steps=0,  # Default value in run_glue.py
                                                    num_training_steps=total_steps)

        # -------------------------------------------------------------------

        # Function to calculate the accuracy of our predictions vs labels
        def flat_accuracy(preds, labels):
            pred_flat = np.argmax(preds, axis=1).flatten()
            labels_flat = labels.flatten()
            return np.sum(pred_flat == labels_flat) / len(labels_flat)

        def flat_precision(preds, labels, num_labels):
            pred_flat = np.argmax(preds, axis=1).flatten()
            labels_flat = labels.flatten()
            return precision_score(labels_flat, pred_flat, average="micro")

        def flat_recall(preds, labels, num_labels):
            pred_flat = np.argmax(preds, axis=1).flatten()
            labels_flat = labels.flatten()
            return recall_score(labels_flat, pred_flat, average="micro")

        def format_time(elapsed):
            '''
            Takes a time in seconds and returns a string hh:mm:ss
            '''
            # Round to the nearest second.
            elapsed_rounded = int(round((elapsed)))

            # Format as hh:mm:ss
            return str(datetime.timedelta(seconds=elapsed_rounded))

        # -------------------------------------------------------------------

        # This training code is based on the `run_glue.py` script here:
        # https://github.com/huggingface/transformers/blob/5bfcd0485ece086ebcbed2d008813037968a9e58/examples/run_glue.py#L128

        # Set the seed value all over the place to make this reproducible.
        seed_val = 42

        random.seed(seed_val)
        np.random.seed(seed_val)
        torch.manual_seed(seed_val)
        torch.cuda.manual_seed_all(seed_val)

        # Store the average loss after each epoch so we can plot them.
        loss_values = []

        # For each epoch...
        for epoch_i in range(0, epochs):

            # ========================================
            #               Training
            # ========================================

            # Perform one full pass over the training set.

            print("")
            print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, epochs))
            print('Training...')

            # Measure how long the training epoch takes.
            t0 = time.time()

            # Reset the total loss for this epoch.
            total_loss = 0

            # Put the model into training mode. Don't be mislead--the call to
            # `train` just changes the *mode*, it doesn't *perform* the training.
            # `dropout` and `batchnorm` layers behave differently during training
            # vs. test (source: https://stackoverflow.com/questions/51433378/what-does-model-train-do-in-pytorch)
            model.train()

            # For each batch of training data...
            for step, batch in enumerate(train_dataloader):

                # Progress update every 40 batches.
                if step % 40 == 0 and not step == 0:
                    # Calculate elapsed time in minutes.
                    elapsed = format_time(time.time() - t0)

                    # Report progress.
                    print(
                        '  Batch {:>5,}  of  {:>5,}.    Elapsed: {:}.'.format(step, len(train_dataloader), elapsed))

                # Unpack this training batch from our dataloader.
                #
                # As we unpack the batch, we'll also copy each tensor to the GPU using the
                # `to` method.
                #
                # `batch` contains three pytorch tensors:
                #   [0]: input ids
                #   [1]: attention masks
                #   [2]: labels
                b_input_ids = batch[0].to(device)
                b_input_mask = batch[1].to(device)
                b_labels = batch[2].to(device)

                # Always clear any previously calculated gradients before performing a
                # backward pass. PyTorch doesn't do this automatically because
                # accumulating the gradients is "convenient while training RNNs".
                # (source: https://stackoverflow.com/questions/48001598/why-do-we-need-to-call-zero-grad-in-pytorch)
                model.zero_grad()

                # Perform a forward pass (evaluate the model on this training batch).
                # This will return the loss (rather than the model output) because we
                # have provided the `labels`.
                # The documentation for this `model` function is here:
                # https://huggingface.co/transformers/v2.2.0/model_doc/bert.html#transformers.BertForSequenceClassification
                outputs = model(b_input_ids,
                                token_type_ids=None,
                                attention_mask=b_input_mask,
                                labels=b_labels)

                # The call to `model` always returns a tuple, so we need to pull the
                # loss value out of the tuple.
                loss = outputs[0]

                # Accumulate the training loss over all of the batches so that we can
                # calculate the average loss at the end. `loss` is a Tensor containing a
                # single value; the `.item()` function just returns the Python value
                # from the tensor.
                total_loss += loss.item()

                # Perform a backward pass to calculate the gradients.
                loss.backward()

                # Clip the norm of the gradients to 1.0.
                # This is to help prevent the "exploding gradients" problem.
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

                # Update parameters and take a step using the computed gradient.
                # The optimizer dictates the "update rule"--how the parameters are
                # modified based on their gradients, the learning rate, etc.
                optimizer.step()

                # Update the learning rate.
                scheduler.step()

            # Calculate the average loss over the training data.
            avg_train_loss = total_loss / len(train_dataloader)

            # Store the loss value for plotting the learning curve.
            loss_values.append(avg_train_loss)

            print("")
            print("  Average training loss: {0:.2f}".format(avg_train_loss))
            print("  Training epcoh took: {:}".format(format_time(time.time() - t0)))

            # ========================================
            #               Validation
            # ========================================
            # After the completion of each training epoch, measure our performance on
            # our validation set.

            print("")
            print("Running Validation...")

        t0 = time.time()

        # Put the model in evaluation mode--the dropout layers behave differently
        # during evaluation.
        model.eval()

        # Tracking variables
        eval_loss, eval_accuracy, eval_precision, eval_recall = 0, 0, 0, 0
        nb_eval_steps, nb_eval_examples = 0, 0

        predictions = list()
        # Evaluate data for one epoch
        for batch in prediction_dataloader:
            # Add batch to GPU
            batch = tuple(t.to(device) for t in batch)

            # Unpack the inputs from our dataloader
            b_input_ids, b_input_mask = batch

            # Telling the model not to compute or store gradients, saving memory and
            # speeding up validation
            with torch.no_grad():
                # Forward pass, calculate logit predictions.
                # This will return the logits rather than the loss because we have
                # not provided labels.
                # token_type_ids is the same as the "segment ids", which
                # differentiates sentence 1 and 2 in 2-sentence tasks.
                # The documentation for this `model` function is here:
                # https://huggingface.co/transformers/v2.2.0/model_doc/bert.html#transformers.BertForSequenceClassification
                outputs = model(b_input_ids,
                                token_type_ids=None,
                                attention_mask=b_input_mask)

            # Get the "logits" output by the model. The "logits" are the output
            # values prior to applying an activation function like the softmax.
            logits = outputs[0]

            # Move logits and labels to CPU
            logits = logits.detach().cpu().numpy()

            # Track the number of batches
            predictions.extend(list(np.argmax(logits, axis=1).flatten()))

            nb_eval_steps += 1

            # Report the final accuracy for this validation run.
        emo = {"joy": 0,
               "sadness": 1,
               "fear": 2,
               "anger": 3,
               "surprise": 4,
               "disgust": 5}
        emo_rev = {val: key for key, val in emo.items()}

        pd.DataFrame.from_dict({"emotion": [emo_rev[p] for p in predictions]})\
            .to_csv("predictions.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data")
    parser.add_argument('--labels','--list', nargs='+', type=str)
    parser.add_argument("--predict")

    args = parser.parse_args()
    name = args.data.split(".")[0]

    device = initiate_bert()
    inputs, masks, dataset = initiate_data(args.data)
    pred_inputs, pred_masks, pred_dataset = initiate_data(args.predict)

    train_predict(inputs, masks, args.labels, dataset, name, device,
                  pred_inputs, pred_masks, pred_dataset)
