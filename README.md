# Chulius : Choosing Julius
This is a wrapper of Julius with robustness.
Julius recognizes speech very usefully, but there takes many false recognition.

This is caused by which Julius gets success on all situations.
Thus, we find that a recognition score can be trusted from its recognition result.
In other words, the score is low when the false recognition occures.

So, Chulius discards low score recognition for robustness.

# Dependencies
- [Python][https://www.python.org/]
- [Julius][https://github.com/julius-speech/julius]

# Example
First, create a dictionally file for speech recognition.
Create and compile a vocaburally file (*.voca) and a grammar file (*.grammar).
We use example at http://www.feijoa.jp/laboratory/raspberrypi/julius/ .

## kaden.voca

    % KADEN
    テレビ   t e r e b i
    電気    d e n k i
    % WO        
    を      w o 
    % PLEASE    
    つけて   t u k e t e
    消して   k e sh i t e
    % NS_B
    [s]     silB
    % NS_E
    [s]     silE


## kaden.grammar

    S      : NS_B KADEN_ PLEASE NS_E
    KADEN_ : KADEN
    KADEN_ : KADEN WO

Next, compile these files.
`mkdfa.pl kaden`

Finally, let us run Chulius on Python.

##  test.py
Class `Chulius` takes arguments as follows:
1. String; Julius executeable file
2. Stting; Julius configure file (*.conf or *.jconf)
3. String; grammar file name (created above)
4. Float; target score

Recognition successes if target score is achieved.
Empirically, about 0.85 is good.
If 0, Chulius equivalents to normal Julius.

    from chulius import Chulius, RecognitionError

    chulius = Chulius('path/to/Julius/julius.exe',
                      'path/to/Julius/hmm_mono.jconf',
                      'path/to/grammar/file/kaden',
                      0.85)
    while True:
        try:
            print(chulius.recognize())
        except RecognitionError:
            print('Recognition Failed')
        except KeyboardInterrupt:
            break
    print('End')
