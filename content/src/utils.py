import numpy as np

def cleanup_df(df):
    df = df.dropna(axis=1, how="all")
    df = df.rename(columns={ 'ITEM/CLR/SKU/ISO/LMPO/G': 'ITEM' })
    return df

def get_cbm_mismatch(df):
    d = df.MSMT.str.split("x", expand=True).astype(float)
    cbm = round((d[0] / 100) * (d[1] / 100) * (d[2] / 100) * df.PKGS, 3)
    result = df.CBM != cbm
    return result

def is_a_columbia_consignee(df):
    COLUMBIA_CONSIGNEES = [
        'AYANCHIN OUTFITTERS',
        'BO CHUAN INDS.',
        'CHOGORI INDIA RETAIL LIMITED',
        'COLUMBIA SPORTSWEAR COMPANY PVT. LTD.',
        'CON TEKS IC VE DIS TIC A S',
        'DRASTOSA COM ART ESPORTIVOS LTDA',
        'FORUS COLOMBIA SAS',
        'FORUS S A',
        'GMG SPORTS SEA PTE LTD',
        'GOZALAN MAGAZCILIK TESKSTILE VE',
        'KASE LOGISTICS (S) PTE LTD',
        'LOGISTAR ',
        'SA AR AT ENTERPRISE',
        'SKYE GROUP PTY LTD',
        'ZHONGSHAN V GROW LOGISTICS CO LTD',
    ]
    return df.CONSIGNEE.isin(COLUMBIA_CONSIGNEES)
    
def get_all_columbia(df):
    columbia = df[is_a_columbia_consignee(df)]
    return columbia

def get_lpp(df):
    df = df[df.CONSIGNEE == 'LPP S.A']
    df = df[['PO', 'STYLE', 'DC CODE', 'ITEM', 'DEST']]
    df = df.set_index('PO')
    df.index = df.index.astype(str).str.strip()
    return df

def normalize_approvals(df):
    df = cleanup_df(df)
    df = df[['Order No', 'Model', 'DC', 'Brand', 'Destination']]
    df = df.rename(columns={
        'Order No': 'PO', 'Model': 'STYLE', 'DC': 'DC CODE', 'Brand': 'ITEM', 'Destination': 'DEST'
    })
    
    conditions = [df.DEST == 'Romania', df.DEST == 'Poland']
    choices = ['CONSTANTA', 'GDANSK']
    df['DEST'] = np.select(conditions, choices, default='')
    
    df = df.set_index('PO')
    df.index = df.index.astype(str).str.strip()
    return df

def find_lpp_discrepencies(df, approval_df):
    approval_subset = approval_df.loc[df.index]
    result = df.compare(approval_subset, keep_shape=False, keep_equal=False, result_names=("Report", "Approval"))

    if result.size > 0:
        print(result)
    else:
        print("==> No discrepancies found between approvals and report!")

def get_ctns_from_seq(seq_str):
    """
    Takes a string containing comma seperated loading sequences.
    Each sequence have dash (-) seperated starting and ending (inclusive) carton number.
    Returns total number of cartons in the sequences
    """
    seq = seq_str.split(",")
    total = 0
    for i in seq:
        a, b = i.split("-")
        total += int(b) - int(a) + 1
    return total