# -*- coding: utf-8 -*-


"""
Created on Thu Jun 14 11:15:21 2018

@author: Tomoharu
"""
from math import sqrt


def sim_distance(prefs, person1, person2):
    #2人とも評価しているアイテムのリストを得る
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1
            
        #両者共に評価しているもの一つもなければ０を返す
        if len(si)==0: return 0
        
        #全ての差の平方を足し合わせる
        sum_of_squares = sum([pow(prefs[person1][item]-prefs[person2][item],  2)
                                for item in prefs[person1] if item in prefs[person2]])
    
    return 1 / (1 + sum_of_squares)

def sim_pearson(prefs, p1, p2):
    #2人とも評価しているアイテムのリストを得る
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item]=1
            
    #要素の数を調べる
    n = len(si)

    #両者共に評価しているもの一つもなければ０を返す
    if len(si)==0: return 0
    
    #全ての嗜好を合計する
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    
    #平方を合計する
    sum1Sq = sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it],2) for it in si])
    
    #積を合計する
    pSum = sum([prefs[p1][it]*prefs[p2][it] for it in si])
    
    #ピアソンによるスコアを計算する
    num = pSum - (sum1 * sum2/n)
    den = sqrt((sum1Sq - pow(sum1,2)/n) * (sum2Sq - pow(sum2,2)/n))
    if den == 0: return 0
    
    r = num / den
    
    return r


#ディクシュナリprefsからpersonにもっともマッチする者たちを返す
#結果の数と類似性関数はオプションのパラメータ
def topMatches(prefs, person, n=5, similarity = sim_pearson):       
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]
    
    #高スコアがリストの最初の方に来るように並び替える
    scores.sort()
    scores.reverse()
    return scores[0:n] 

#person以外の全ユーザの評点の重み付き平均を使い，personへの推薦を算出する
def getRecommendations(prefs, person, similarity  = sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        #自分自身とは比較しない
        if other == person: continue
        sim = similarity(prefs, person, other)
        
        
        #0以下のスコアは無視する
        if sim <=0: continue
    
        for item in prefs[other]:
            #まだ見ていない映画の得点のみを算出
            if item not in prefs[person] or prefs[person][item]==0:
                #類似度　＊　スコア
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item]*sim
                #類似度を合計
                simSums.setdefault(item,0)
                simSums[item] += sim
                
    #正規化したリストを作る
    rankings = [(total/simSums[item], item) for item, total in totals.items()]
    
    #ソート済みのリストを返す
    rankings.sort()
    rankings.reverse()
    return rankings

#ディクシュナリの要素と引用を入れ替える
def transformPrefs(prefs):
    result ={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            #itemとpersonを入れ替える
            result[item][person] = prefs[person][item]
    return result

def calculateSimilarItems(prefs, n = 10):
    result = {}
    
    #嗜好の行列をアイテム中心な形に反転させる
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        #巨大なデータセット用にステータスを表示
        c += 1
        if c % 100 == 0: print("%d / %d" % (c, len(itemPrefs)))
        #このアイテムに最も似ているアイテムたちを探す
        scores = topMatches(itemPrefs, item, n = n, similarity = sim_distance)
        result[item] = scores
    return result


def loadMovieLens(path = './/ml-100k'):
    #映画のタイトルを得る
    movies = {}
    for line in open(path + '//u.item', errors='ignore'):
        (movieid, title) = line.split('|')[0:2]
        movies[movieid] = title
        
    #データの読み込み
    prefs = {}
    i = 0
    for line in open(path + '//u.data'):
        (userId, movieid, rating, timestamp) = line.split('\t')
        prefs.setdefault(userId, {})
        if i != 0:
            prefs[userId][movies[movieid]] = float(rating)
        i = 1
    return prefs
            
def getRecomendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    
    #このユーザに評価されたアイテムをループする
    for (item, rating) in userRatings.items():
        
        #このアイテムに似ているアイテムたちをループする
        for (similarity, item2) in itemMatch[item]:
            
            #このアイテムに対してユーザがすでに評価を行って入れば無視する
            if item2 in userRatings: continue
        
            #評点と類似度を掛け合わせたものの合計で重み付けする
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            
            #全ての類似度の合計
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
            
    #正規化のため，それぞれ重み付けしたスコアの類似度の合計で割る
    rankings = [(score/totalSim[item], item) for item, score in scores.items()]
            
    #降順に並べたランキングを返す
    rankings.sort()
    rankings.reverse()
    return rankings
            

prefs = loadMovieLens()
#知りたいユーザーの番号を入力する
t1 = getRecommendations(prefs, '**')[0:30]
#アイテムベースの推薦書をディクシュナリ形式で返す
itemsim = calculateSimilarItems(prefs, n = 50)

    

