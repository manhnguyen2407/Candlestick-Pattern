import yfinance as yf
df = yf.download('HPG.VN', start='2023-03-17', end='2024-09-29')


df['BodyHi'] = df.apply(lambda row: max(row['Open'], row['Close']), axis=1)
df['BodyLo'] = df.apply(lambda row: min(row['Open'], row['Close']), axis=1)
df['Body'] = df['BodyHi'] - df['BodyLo']
df['UpShadow'] = df['High'] - df['BodyHi']
df['DnShadow'] = df['BodyLo'] - df['Low']
df['Range'] = df['High'] - df['Low']

def DojiBody(row):
    return row['Range'] > 0 and row['Body'] < (row['Range'] * 0.05 / 100)

df['DojiBody'] = df.apply(DojiBody, axis = 1)
 
def SpinningTopBlack(row):
    return row['DnShadow'] >= (row['Range'] / 100 * 34 ) \
        and row['UpShadow'] > (row['Range'] / 100 * 34 ) \
            and row['DojiBody'] is False \
                and row['Close'] > row['Open']

df['SpinningTopBlack'] = df.apply(SpinningTopBlack, axis = 1)

print(df['SpinningTopBlack'])




