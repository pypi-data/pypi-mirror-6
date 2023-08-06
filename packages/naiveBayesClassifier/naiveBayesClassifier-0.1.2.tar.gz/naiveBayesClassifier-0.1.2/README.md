naive-bayes-classifier
======================

yet another general purpose naive bayesian classifier. (under heavy development)

##Example



```python
"""
Suppose you have some texts of news and know their categories.
You want to train a system with this pre-categorized/pre-classified 
texts. So, you have better call this data your training set.
"""
from naiveBayesClassifier import tokenizer
from naiveBayesClassifier.trainer import Trainer
from naiveBayesClassifier.classifier import Classifier

newsTrainer = Trainer(tokenizer)

# You need to train the system passing each text one by one to the trainer module.
newsSet =[
    {'text': 'not to eat too much is not enough to lose weight', 'category': 'health'},
    {'text': 'Russia try to invade Ukraine', 'category': 'politics'},
    {'text': 'do not neglect exercise', 'category': 'health'},
    {'text': 'Syria is the main issue, Obama says', 'category': 'politics'},
    {'text': 'eat to lose weight', 'category': 'health'},
    {'text': 'you should not eat much', 'category': 'health'}
]

for news in newsSet:
    newsTrainer.train(news['text'], news['category'])

# When you have sufficient trained data, you are almost done and can start to use
# a classifier.
newsClassifier = Classifier(newsTrainer.data, tokenizer)

# Now you have a classifier which can give a try to classifiy text of news whose
# category is unknown, yet.
classification = newsClassifier.classify("Even if I eat too much, is'n it possible to lose some weight")

# the classification variable holds the detected categories sorted
print classification
```

##What is Naive Bayes Theorem and Classifier
It is needles to explain everything once again here. Instead, one of the most eloquent explanations is quoted here.

The following explanation is quoted from [another Bayes classifier][1] which is written in Go. 

>  BAYESIAN CLASSIFICATION REFRESHER: suppose you have a set  of classes
> (e.g. categories) C := {C_1, ..., C_n}, and a  document D consisting
> of words D := {W_1, ..., W_k}.  We wish to ascertain the probability
> that the document  belongs to some class C_j given some set of
> training data  associating documents and classes.
> 
>  By Bayes' Theorem, we have that
> 
>     P(C_j|D) = P(D|C_j)*P(C_j)/P(D).
> 
>  The LHS is the probability that the document belongs to class  C_j
> given the document itself (by which is meant, in practice,  the word
> frequencies occurring in this document), and our program  will
> calculate this probability for each j and spit out the  most likely
> class for this document.
> 
>  P(C_j) is referred to as the "prior" probability, or the  probability
> that a document belongs to C_j in general, without  seeing the
> document first. P(D|C_j) is the probability of seeing  such a
> document, given that it belongs to C_j. Here, by assuming  that words
> appear independently in documents (this being the   "naive"
> assumption), we can estimate
> 
>     P(D|C_j) ~= P(W_1|C_j)*...*P(W_k|C_j)
> 
>  where P(W_i|C_j) is the probability of seeing the given word  in a
> document of the given class. Finally, P(D) can be seen as   merely a
> scaling factor and is not strictly relevant to  classificiation,
> unless you want to normalize the resulting  scores and actually see
> probabilities. In this case, note that
> 
>     P(D) = SUM_j(P(D|C_j)*P(C_j))
> 
>  One practical issue with performing these calculations is the 
> possibility of float64 underflow when calculating P(D|C_j), as 
> individual word probabilities can be arbitrarily small, and  a
> document can have an arbitrarily large number of them. A  typical
> method for dealing with this case is to transform the  probability to
> the log domain and perform additions instead  of multiplications:
> 
>    log P(C_j|D) ~ log(P(C_j)) + SUM_i(log P(W_i|C_j))
> 
>  where i = 1, ..., k. Note that by doing this, we are discarding  the
> scaling factor P(D) and our scores are no longer  probabilities;
> however, the monotonic relationship of the  scores is preserved by the
> log function.

If you are very curious about Naive Bayes Theorem, you may find the following list helpful:

* [Insect Examples][2]
* [Stanford NLP - Bayes Classifier][3]


## TODO
* inline docs
* unit-tests


## AUTHORS
* Mustafa Atik @muatik
* Nejdet Yucesoy @nejdetckenobi


  [1]: https://github.com/jbrukh/bayesian/blob/master/bayesian.go
  [2]: http://www.cs.ucr.edu/~eamonn/CE/Bayesian%20Classification%20withInsect_examples.pdf
  [3]: http://nlp.stanford.edu/IR-book/html/htmledition/naive-bayes-text-classification-1.html