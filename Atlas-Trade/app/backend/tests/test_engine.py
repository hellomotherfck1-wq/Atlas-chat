from atlas.engine import ema, rsi, analyze_klines

def sample():
    rows=[]
    for i in range(40):
        close=100+i*0.4
        rows.append([i,close-0.2,close+0.5,close-0.5,close,1000,i])
    rows.append([41,116,117,115,116,1000,41])
    return rows

def test_ema_is_calculated():
    assert round(ema([1,2,3,4,5],3),2)==4.0

def test_rsi_uptrend():
    assert rsi([float(i) for i in range(20)])==100

def test_only_closed_candles_are_analyzed():
    result=analyze_klines(sample(),"TESTUSDT")
    assert result["symbol"]=="TESTUSDT"
    assert result["decision"] in {"AL","BEKLE"}

def test_insufficient_data_never_buys():
    assert analyze_klines([[0,1,1,1,1,1,0]]*10,"X")["decision"]=="BEKLE"
