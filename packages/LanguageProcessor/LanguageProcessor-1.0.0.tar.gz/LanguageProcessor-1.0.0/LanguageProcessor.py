
from ChemTagger import ChemTagger
from NaiveBayes import NaiveBayes
import pickle
import os.path as op
from math import log10
from random import shuffle

class LanguageProcessor():    
        
    def __init__(self, decisions=None, processors=None):
        self.tagger = ChemTagger()
        self.decisions = decisions
        self.processors = processors
        if not self.processors == None:
            for tag_type in self.processors.keys():
                for process in self.processors[tag_type].keys():
                    file = self.processors[tag_type][process]
                    self.processors[tag_type][process] = self.loadLanguageModel(file)

    def extractAttributes(self, item_features, selected_attributes):
        attributes = {}
        for item in selected_attributes:
            if item in item_features:
                attributes[item] = 'True'
            else:
                attributes[item] = 'False'
        return(attributes)

    def loadLanguageModel(self, file):
        if not op.isfile(file):
            raise Exception("\'" + file + "\' is not a file")
        with open(file, 'rb') as fh:
            lang_model = pickle.load(fh)
        if not isinstance(lang_model, NaiveBayes):
            raise Exception("\'" + file + "\' is not a valid language model")
        return(lang_model)    
        
    def identify_type(self, label):
        l_type = set()
        if self.decisions == None:
            raise Exception("No decisions defined")
        for decision in self.decisions:
            if not decision[0].match(label) == None:
                l_type.add(decision[1])
        return(l_type)
    
    def formatNumber(self, number):
        return("{0:.6f}".format(number))
    
    def addNumbers(self, number1, number2):
        return(self.formatNumber(float(number1) + float(number2)))
    
    def prodNumbers(self, numbers):
        prod = 1
        for number in numbers:
            prod *= float(number)
        return(self.formatNumber(prod))
    
    def compilePositionProxies(self, left, right):
        missing1 = 3 - len(left)
        missing2 = 3 - len(right)
        for i in range(missing1):
            left.add("#S" + str(i + 1))
        for i in range(missing2):
            right.add("#E" + str(i + 1))        
        return(";".join(left) + ";" + ";".join(right))
    
    def defaultScoring(self, catagories, samples=1000):
        max_length = None
        c = len(catagories.keys())
        for catagory in catagories.keys():
            length = len(catagories[catagory])
            if max_length == None:
                max_length = length
            if max_length > length:
                max_length = length
        N = c * max_length * samples
        feature_counts = {}
        for i in range(samples):
            for catagory in catagories.keys():
                if not catagory in feature_counts.keys():
                    feature_counts[catagory] = {}
                shuffle(catagories[catagory])
                for j in range(max_length):
                    for word in set(catagories[catagory][j]):
                        if not word in feature_counts[catagory].keys():
                            feature_counts[catagory][word] = 0
                        feature_counts[catagory][word] += 1
        contribution = {}
        for catagory in feature_counts.keys():
            for word in feature_counts[catagory].keys():
                if not word in contribution.keys():
                    contribution[word] = 0
                contribution[word] += feature_counts[catagory][word]
        scores = {}
        #statistics = {}
        for word in contribution.keys():
            scores[word] = (contribution[word] / N) * log10(N / (1 + contribution[word]))
            #statistics[word] = [contribution[word], N]
        sorted_features = sorted(scores, key=scores.get, reverse=True)
        return(sorted_features, scores)

    def getConfusionMatrix(self, actual, predicted):
        confusion_matrix = {}
        if not len(predicted) == len(actual):
            raise Exception("Actual and predicted not of the same size")
        length = len(predicted)
        for i in range(length):
            if not actual[i] in confusion_matrix.keys():
                confusion_matrix[actual[i]] = {}
            if not predicted[i] in confusion_matrix[actual[i]].keys():
                confusion_matrix[actual[i]][predicted[i]] = 0
            confusion_matrix[actual[i]][predicted[i]] += 1
        return(confusion_matrix)

    def accuracy(self, confusion_matrix):
        true = 0
        total = 0
        measures = {}
        for actual in confusion_matrix.keys():
            l_true = 0
            l_total = 0
            for predicted in confusion_matrix[actual].keys():
                if actual == predicted:
                    true += confusion_matrix[actual][predicted]
                    l_true += confusion_matrix[actual][predicted]
                l_total += confusion_matrix[actual][predicted]
                total += confusion_matrix[actual][predicted]
            l_ac = l_true / l_total
            measures[actual] = l_ac
        measures['model'] = true / total
        return(measures)
    
    def macroF1(self, confusion_matrix):
        measures = {}
        fp = {}
        for actual in confusion_matrix.keys():
            tp = 0
            fn = 0
            for prediction in confusion_matrix[actual].keys():
                if actual == prediction:
                    tp = confusion_matrix[actual][prediction]
                else:
                    fn += confusion_matrix[actual][prediction]
                    if not prediction in fp.keys():
                        fp[prediction] = 0
                    fp[prediction] += confusion_matrix[actual][prediction]
            measures[actual] = {'tp' : tp, 'fn' : fn, 'fp' : 0}
        for prediction in fp.keys():
            if not prediction in measures.keys():
                measures[prediction] = {'tp' : 0, 'fn' : 0}
            measures[prediction]['fp'] = fp[prediction]
        precision = 0
        recall = 0
        for label in measures.keys():
            precision += measures[label]['tp'] / (measures[label]['tp'] + measures[label]['fp'])
            recall += measures[label]['tp'] / (measures[label]['tp'] + measures[label]['fn'])
        precision /= len(measures.keys())
        recall /= len(measures.keys())
        return(2 * (precision * recall) / (precision + recall))
    
    def processTagText(self, ref, text):        
        paragraph_tags = self.tagger.tagParagraph(text)
        output_tags = []
        for tag in paragraph_tags:
            labels = ';'.join(set(tag[3]))
            output_tags.append([ref, str(tag[0]), tag[1], tag[2], labels, text[tag[1]:tag[2]]])
        return(output_tags)
    
    def compileFeatures(self, text, tags):
        tagged_sentences = self.tagger.getTaggedSentences(text, tags)
        proxi_features = self.tagger.getProximityFeatures(tagged_sentences)
        if not len(tagged_sentences) == len(proxi_features):
            raise Exception("Feature discontinuation detected")
        proxi_dictionary = {}
        for tag in proxi_features:
            proxi_dictionary[tag[0]] = set(self.compilePositionProxies(tag[4], tag[5]).split(";"))
        features = {}
        for tag in tagged_sentences:
            features[tag[0]] = [self.identify_type(tag[3]), self.tagger.getWordFeatures(tag[4]), proxi_dictionary[tag[0]]]
        return([self.tagger.getWordFeatures(text), features])
    
    def compileFeatureVector(self, text, tags, labels=None):
        (abstract, positions) = self.compileFeatures(text, tags)
        lv = lambda label, vector: [label + '#' + v for v in vector]
        vectors = []
        for p in positions:
            label = None
            if not labels == None:
                if p in labels.keys():
                    label = labels[p]
            l_type = positions[p][0]
            features = lv('A', abstract)
            for item in lv('S', positions[p][1]):
                features.append(item)
            for item in lv('P', positions[p][2]):
                features.append(item)
            vectors.append([l_type, p, label, features])
        return(vectors)
    
    def compilePairFeatureVectors(self, pairs, text, tags):    
        vectors = {}
        for vector in self.compileFeatureVector(text, tags):
            if not vector[1] in vectors.keys():
                vectors[vector[1]] = []
            vectors[vector[1]].append(vector[3])
        label_to_positions = {}
        for tag in tags:
            if not tag[4] in label_to_positions.keys():
                label_to_positions[tag[4]] = set()
            label_to_positions[tag[4]].add(str(tag[2]) + '-' + str(tag[3]))
        def getFeatureVector(prefix, label):
            output_vectors = []
            for position in label_to_positions[label]:
                for v in vectors[position]:
                    for i in range(len(v)):
                        r_prefix = prefix + '#'
                        if not r_prefix in v[i]:
                            v[i] = r_prefix + v[i]                    
                    output_vectors.append(v)
            return(output_vectors)    
        all_combinations = {}
        for pair in pairs:
            ref = pair[0] + "=>" + pair[1]
            all_combinations[ref] = []
            source = getFeatureVector("source", pair[0])
            target = getFeatureVector("target", pair[1])
            for t in target:
                target_space = set(t)
                for s in source:
                    feature_space = target_space
                    for e in s:
                        feature_space.add(e)
                    all_combinations[ref].append(feature_space)    
        return(all_combinations, label_to_positions)
    
    def determinePairLabelValue(self, source_positions, target_positions, label_values):
        def getMostUsedLabel(positions):
            label_count = {}
            for p in positions:
                if not p in label_values.keys():
                    return(None)              
                value = label_values[p]                
                if not value in label_count.keys():
                    label_count[value]=0
                label_count[value] += 1
            labelValues = sorted(label_count.keys(), key = lambda x: label_count[x], reverse=True)
            return(labelValues[0])
        s = getMostUsedLabel(source_positions)
        t = getMostUsedLabel(target_positions)
        if s == None or t == None:
            return(None)
        return(sorted([s,t])[0])
    
    def processPairLangauge(self, process_path, pairs, text, tags):
        if self.processors == None:
            raise Exception("No processors defined")  
        (features, label_to_positions) = self.compilePairFeatureVectors(pairs, text, tags)
        scores = {}
        for pair in pairs:
            ref = pair[0] + "=>" + pair[1]
            if not ref in scores.keys():
                scores[ref] = []
                model = self.processors[process_path[0]][process_path[1]]
                for feature in features[ref]:
                    attributes = self.extractAttributes(feature, model.attributes)
                    scores[ref].append(model.preferredLabel(model.predict({'attributes' : attributes })))   
        return(scores)
    
    def processTagLangauge(self, text, tags):
        if self.processors == None:
            raise Exception("No processors defined")  
        scores = {}
        for vector in self.compileFeatureVector(text, tags):
            if not vector[1] in scores.keys():
                scores[vector[1]] = {} 
            for processor in self.processors[vector[0]]:
                model = self.processors[vector[0]][processor]
                attributes = self.extractAttributes(vector[3], model.attributes)
                if not processor in scores[vector[1]].keys():
                    scores[vector[1]][processor] = model.preferredLabel(model.predict({'attributes' : attributes }))
        return(scores)
    
    def split_seq(self, seq, size):
        newseq = []
        splitsize = 1.0 / size * len(seq)
        for i in range(size):
                newseq.append(seq[int(round(i * splitsize)):int(round((i + 1) * splitsize))])
        return newseq
    
    def balanced_execution(self, data, features, cross_fold=10, smoothing=1 / 3):    
        max_length = None    
        for catagory in data.keys():
            length = len(data[catagory])
            if max_length == None:
                max_length = length
            if max_length > length:
                max_length = length
        data_subset = []
        for catagory in data.keys():
            shuffle(data[catagory])
            for i in range(max_length):
                data_subset.append([data[catagory][i], catagory])
        shuffle(data_subset)
        parts = self.split_seq(data_subset, cross_fold)
        actual_labels = []
        predicted_labels = []     
        for i in range(cross_fold):        
            eval_set = parts[i]
            train_set = []
            for j in range(cross_fold):
                if not i == j:
                    for item in parts[j]:
                        train_set.append(item)
            model = NaiveBayes()
            for f in features:
                model.set_smoothing({f:smoothing})
            for item in train_set:
                attributes = self.extractAttributes(item[0], features)
                model.add_instances({'attributes':attributes, 'label' : item[1], 'cases' : 1})
            model.train()   
            for item in eval_set:
                attributes = self.extractAttributes(item[0], features)
                predicted_labels.append(model.preferredLabel(model.predict({'attributes' : attributes })))
                actual_labels.append(item[1])
        model = NaiveBayes()
        for f in features:
            model.set_smoothing({f:smoothing})
        for item in data_subset:
            attributes = self.extractAttributes(item[0], features)
            model.add_instances({'attributes':attributes, 'label' : item[1], 'cases' : 1})
        model.train()
        return(self.getConfusionMatrix(actual_labels, predicted_labels), model)
    
    def one_feature_reduction(self, data, features, cross_fold=10, smoothing=1 / 3):       
        (start_confusion, start_model) = self.balanced_execution(data, features, cross_fold, smoothing)
        start_f1 = self.macroF1(start_confusion)
        remove_penalty = {}
        for feature in features:
            test_features = set(features)
            test_features.remove(feature)
            (confusion_matrix, run_model) = self.balanced_execution(data, list(test_features), cross_fold, smoothing)
            f1 = self.macroF1(confusion_matrix)
            remove_penalty[feature] = f1 - start_f1
        remove_feature = sorted(remove_penalty, key=lambda x: remove_penalty[x])[0]
        return(remove_feature, remove_penalty[remove_feature])


