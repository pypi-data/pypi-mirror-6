
import re
import shelve
import os

class ChemTagger():
    
    def __init__(self, caseSensitive=False, shelveFile=None, shelveWriteback=True, create=False):
        self.greek = {'\u03B1':'alpha', '\u03B2':'beta', '\u03B3':'gamma', '\u03B4':'delta', '\u03B5':'epsilon', '&' : 'and'}
        self.regexp_early_reduce = re.compile("[^a-z|^A-Z|^0-9|^\+|^\-|^\=|^\/||^\.]")
        self.regexp_late_reduce = re.compile("[^a-z|^A-Z|^0-9|^\+|^\-|^\=|^\/|]|s+$")
        self.ssplit = re.compile('(\.)\s+([A-Z|\d])')
        self.spacecu = re.compile('\s+')  
              
        self.regexp_blacklist = [
         re.compile("^.{0,2}$"),
         re.compile("^\w\-\w?$"),
         re.compile("^[\+|\-]+$"),
         re.compile("^\d{2,3}$"),
         re.compile("^\w{1,2}\d{1,3}$"),
         re.compile("^\d{1,3}\w{1,2}$"),
         re.compile("^group\s*[\w|\d]*$"),
         re.compile("^compound\s*[\w|\d]*$"),
         re.compile("^substances*\s*[\w|\d]*$"),
         re.compile("^anti.*$"),
         re.compile("^.*yl$"),
         re.compile("^.*lic$"),
         re.compile("^.*group$"),
         re.compile("^.*vector$"),
         re.compile("^.*cide$"),
         re.compile("^.*gen$"),
         re.compile("^.*inhibitor$"),
         re.compile("^.*compound$") ] 
               
        self.set_blacklist = set()
        self.set_blacklist.add("and")
                
        self.shelveFile = shelveFile 
        self.caseSensitive = caseSensitive
        shelveFlag = 'r'
        self.dictionary = {}
        if not self.shelveFile == None:
            if not create and not os.path.isfile(self.shelveFile):
                raise Exception("Shelve file: \'" + self.shelveFile + "\' does not exist")
            elif create:
                if os.path.isfile(self.shelveFile):
                    os.remove(self.shelveFile)
                shelveFlag = 'c'
            self.dictionary = shelve.open(self.shelveFile, flag=shelveFlag, writeback=shelveWriteback)
                
    def wordfilter(self, reduced):
        a = reduced in self.set_blacklist
        if not a:
            for regexp in self.regexp_blacklist:
                if regexp.match(reduced):
                    a = 1
                    break
        return(a)
       
    def closeShelve(self):
        self.dictionary.close()
        
    def openWriteShelve(self):
        self.dictionary.close()
        self.dictionary = shelve.open(self.shelveFile, flag='w', writeback=True)                                      
  
    def prepareWords(self, text, full=False):
        for g in self.greek.keys():
            text = text.replace(g, self.greek[g])
        if not self.caseSensitive:
            text = text.lower()
        words = self.trimText(text).split(' ')
        prepared_words = []
        length = len(words) - 1
        for i in range(length + 1):
            if i == length or full:
                late = self.regexp_late_reduce.sub('', words[i])
                if not late == '':
                    prepared_words.append(late)
            else:
                early = self.regexp_early_reduce.sub('', words[i])
                if not early == '':
                    prepared_words.append(early)
        return(prepared_words)
    
    def trimText(self, text):
        return(self.spacecu.sub(' ', text).strip())
    
    def populateDictionary(self, dictionary, words, label):
        if not words[0] in dictionary.keys():
            dictionary[words[0]] = { '*' : {}, '#' : [] }   
        if len(words) == 1:
            if not label in dictionary[words[0]]['#']:
                dictionary[words[0]]['#'].append(label)
        elif len(words) > 1:
            self.populateDictionary(dictionary[words[0]]['*'], words[1:], label)

    def stopByRegularExpression(self, regexp):
        self.regexp_blacklist.append(re.compile(regexp.strip()))
        
    def stopByWord(self, word):
        self.set_blacklist.add(word.strip())

    def addInstance(self, text, label):
        prepared_words = self.prepareWords(text)
        if not self.wordfilter(' '.join(prepared_words)):
            if len(prepared_words) > 0:
                self.populateDictionary(self.dictionary, prepared_words, label)
                        
    def searchDictionary(self, dictionary, words):
        childs = -1
        if words[0] in dictionary.keys():          
            if len(words) == 1:
                return(len(dictionary[words[0]]['*'].keys()), dictionary[words[0]]['#'])
            elif len(words) > 1:
                return(self.searchDictionary(dictionary[words[0]]['*'], words[1:]))
        else:
            return(childs, [])

    def lookupWord(self, words):
        prepared_words = self.prepareWords(' '.join(words))
        (childs, labels) = self.searchDictionary(self.dictionary, prepared_words)
        return(childs, labels)

    def tagSentence(self, words):
        tags = []
        length = len(words)
        skip = 0
        for i in range(length):
            j = i + skip
            if j >= length:
                break
            (childs, labels) = self.lookupWord([words[j]]) 
            k = j + 1
            l = k
            tmp_childs = childs
            while tmp_childs > 0 and k < length:
                k += 1
                (tmp_childs, tmp_labels) = self.lookupWord(words[j:k])
                if tmp_childs == -1:
                    break
                elif len(tmp_labels) > 0:
                    childs = tmp_childs
                    labels = tmp_labels
                    skip = k - i - 1
                    l = k
                    if tmp_childs == -1:
                        break
            if len(labels) > 0:
                tags.append([childs, j, l, labels])
        return(tags)
    
    def splitParagraph(self, paragraph):
        data = self.ssplit.split(self.trimText(paragraph))
        i = len(data)
        for j in range(i):
            if data[j] == '.' and j > 0:
                data[j - 1] += data[j]
                data[j] = ''
            elif len(data[j]) == 1 and j + 1 < i:
                data[j + 1] = data[j] + data[j + 1]
                data[j] = ''
        sentences = []
        for k in range(i):
            if not data[k] == '':
                sentences.append(data[k])
        return(sentences)    
    
    def updatePositions(self, tags, words, offset):
        position = 0
        for i in range(0, tags[1]):
            position += len(words[i]) + 1
        start = position
        for i in range(tags[1], tags[2]):
            position += len(words[i]) + 1
        end = position - 1
        tags[1] = start + offset
        tags[2] = end + offset

    def tagParagraph(self, paragraph):
        position = 0
        tags = []
        for sentence in self.splitParagraph(paragraph):
            words = []
            for word in sentence.split(' '):
                if not word == '':
                    words.append(word)
            for tag in self.tagSentence(words):
                self.updatePositions(tag, words, position)
                tags.append(tag)
            position += len(sentence) + 1
        return(tags)
     
    def getWordFeatures(self, text):
        return(set(self.prepareWords(text, full=True)))
               
    def getTaggedSentences(self, text, tags):
        sentences = self.splitParagraph(text)
        taggedSentences = []
        smax = 0
        index_counter = -1
        index_length = -1
        cur_length = 0
        for tag in tags:
            if smax < tag[3]:
                smax = tag[3]
            else:
                raise Exception('Discontinuation detected for ' + tag[0])
            while index_length < smax:
                index_counter += 1
                cur_length = index_length + 1
                index_length += len(sentences[index_counter]) + 1
            taggedSentences.append([str(tag[2]) + "-" + str(tag[3]), tag[2] - cur_length, tag[3] - cur_length, tag[4], sentences[index_counter]])
        return(taggedSentences)    

    def getProximityFeatures(self, taggedSentences, cluster=1, backwards= -3, forwards=3):
        features = []
        if backwards > 0 or forwards < 0:
            raise Exception('Invalid backward and/or forward counts')
        for tag in taggedSentences:
            left = tag[4][:tag[1]].split(' ')[(backwards - 1):-1]
            right = tag[4][tag[2]:].split(' ')[1:(forwards + 1)]
            start_pos = tag[1] - len(' '.join(left))
            if not len(left) == 0:
                start_pos -= 1
            end_pos = tag[2] + len(' '.join(right))
            if not len(right) == 0:
                end_pos += 1
            features.append([tag[0], start_pos, end_pos, tag[3], self.getWordFeatures(' '.join(left)), self.getWordFeatures(' '.join(right)) ])                                     
        if cluster == 1:
            groups = {}
            for i in range(len(features)):
                if not features[i][0] in groups.keys():
                    groups[features[i][0]] = []
                groups[features[i][0]].append(i)
            chains = []
            for index in groups.keys():
                chain = []
                for i in groups[index]:                    
                    for j in groups[index]:
                        if i == j:
                            break
                        if features[j][1] < features[i][2] and features[i][1] < features[j][2]:
                            chain.append(i)
                            chain.append(j)
                if len(chain) > 0:
                    chains.append(sorted(set(chain)))
            for chain in chains:
                for item in chain:
                    features[item][1] = features[chain[0]][1]
                    features[item][2] = features[chain[-1]][2]
                    features[item][4] = features[chain[0]][4]
                    features[item][5] = features[chain[-1]][5]                 
        return(features)
    
    def CorrectName(self,name):
        if len(name)>3:
            if 'content' in name.lower():
                p = name.lower().find('content')
                name = name[:p].strip()
            a = name[-2] == 'r' or  name[-2] == 's' or name[-2] == 'k' or name[-2] == 'm' or name[-2]=='t'
            b = name[-1] == 'e' or name[-1] == 'i'
            if not a and b:
                my_name = name + "s"
            else:
                my_name = name
            if name[-2] == 's' and name[-1] == 'i':
                my_name = name + 's'
            if name[-2] == 'o' and name[-1] == 'e':
                my_name = name + 's'
            if name[-3] == 'e' and name[-2] == 't' and name[-1] == 'e':
                my_name = name + 's'
            return(my_name)
        else:
            return(name)
            
        
