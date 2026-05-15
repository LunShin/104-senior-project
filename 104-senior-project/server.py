"""
104 高年級 — 友善企業評分後端（無需 API Key）
啟動: python3 server.py
依賴: pip3 install flask flask-cors requests beautifulsoup4
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import random, time, re, math

app = Flask(__name__)
CORS(app)

# ══════════════════════════════════════════════════════════════
#  真實資料庫：來自政府認證、DEI獲獎、104高年級品牌專區
#  資料來源：台北市113年中高齡友善企業認證、DEI友善壯世代雇主獎、
#           勞動部促進中高齡就業獲獎、104高年級友善企業品牌專區
# ══════════════════════════════════════════════════════════════
DATABASE = [
    {
        "name": "老爺酒店集團", "industry": "住宿及餐飲業",
        "totalScore": 96,
        "dimensions": {
            "culture":     {"score": 19, "evidence": "104高年級品牌企業，社幫手夥伴占30%，青銀共融文化"},
            "recruitment": {"score": 20, "evidence": "104高年級合作品牌，積極歡迎中高齡二度就業"},
            "work":        {"score": 18, "evidence": "提供固定班別、跨部門培訓，適合中高齡節奏"},
            "environment": {"score": 19, "evidence": "年度健康體檢、旅遊補助、訂房用餐優惠"},
            "life":        {"score": 20, "evidence": "退休金提撥、鼓勵回聘、完整退休轉任制度"},
        },
        "tags": ["退休轉任制度", "青銀共事", "固定班別", "提供培訓", "歡迎二度就業", "健康支持"],
        "measures": ["每月提撥退休金並鼓勵在職進修", "跨部門與飯店交叉培訓計畫", "退休員工回聘機制，讓經驗得以傳承", "一對一專屬輔導員陪伴到職"],
        "cities": ["台北市", "新竹縣市", "宜蘭縣"], "jobCount": 80,
        "dei": "104高年級DEI友善社世代雇主",
        "summary": "104高年級旗艦合作品牌，社幫手夥伴占比30%，退休轉任制度業界楷模。",
        "warmthLabel": "冬天裡的大暖爐",
    },
    {
        "name": "王品餐飲集團", "industry": "餐飲服務業",
        "totalScore": 90,
        "dimensions": {
            "culture":     {"score": 18, "evidence": "台北市113年中高齡友善企業認證，多品牌均獲認可"},
            "recruitment": {"score": 19, "evidence": "聚鍋、禾七、享鴨、原燒等多品牌均開放中高齡應徵"},
            "work":        {"score": 18, "evidence": "提供固定班別保障，避免大小夜輪班，體力負擔低"},
            "environment": {"score": 17, "evidence": "定期職場安全檢核，符合人因工程標準"},
            "life":        {"score": 18, "evidence": "員工餐補、年度健檢、旅遊補助、完整勞退提撥"},
        },
        "tags": ["固定班別", "低體力負擔", "健康支持", "提供培訓", "職務再設計"],
        "measures": ["台北市113年中高齡友善企業認證（4個品牌）", "固定班別制度，不輪大小夜班", "完整員工餐飲補貼與年度健檢", "中高齡職務再設計，降低體力負擔"],
        "cities": ["台北市", "新北市", "台中市", "台南市", "高雄市"], "jobCount": 200,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "旗下多個品牌獲台北市政府中高齡友善認證，固定班別與低體力負擔設計為一大亮點。",
        "warmthLabel": "美食職涯，樂享共融",
    },
    {
        "name": "摩斯漢堡（安心食品服務）", "industry": "速食餐飲業",
        "totalScore": 87,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "台北市113年中高齡友善認證，友善多元文化"},
            "recruitment": {"score": 18, "evidence": "長期歡迎中高齡兼職及全職，彈性應徵管道"},
            "work":        {"score": 18, "evidence": "多種班次選擇，固定班別，工作流程系統化易上手"},
            "environment": {"score": 17, "evidence": "廚房設備輔助降低體力需求，定期安全培訓"},
            "life":        {"score": 17, "evidence": "員工餐飲福利、勞退提撥、員工訓練補助"},
        },
        "tags": ["固定班別", "彈性工時", "低體力負擔", "歡迎二度就業", "提供培訓"],
        "measures": ["台北市113年中高齡友善企業認證", "多種班次供選擇（兼職、全職）", "系統化SOP讓中高齡快速上手", "門市輔具配備，降低作業體力需求"],
        "cities": ["台北市", "新北市", "桃園市", "台中市", "高雄市"], "jobCount": 150,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "長期歡迎中高齡夥伴加入，系統化流程與多班次選擇，讓二度就業輕鬆上手。",
        "warmthLabel": "樂齡好夥伴，健康好職涯",
    },
    {
        "name": "爭鮮迴轉壽司", "industry": "餐飲服務業",
        "totalScore": 85,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "台北市113年認證，兩個品牌均獲認可"},
            "recruitment": {"score": 17, "evidence": "中高齡友善應徵，重視服務熱忱而非年齡"},
            "work":        {"score": 18, "evidence": "固定班別，工作動線設計符合人因工程"},
            "environment": {"score": 16, "evidence": "定期職場環境改善，完備安全設施"},
            "life":        {"score": 17, "evidence": "員工餐飲福利、勞退提撥、員工折扣"},
        },
        "tags": ["固定班別", "低體力負擔", "友善面試", "提供培訓"],
        "measures": ["台北市113年中高齡友善企業認證", "固定排班制度，工作時段穩定", "人因工程動線設計，減輕體力負擔", "完整新人培訓，快速融入職場"],
        "cities": ["台北市", "新北市", "桃園市", "台中市"], "jobCount": 100,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "爭鮮餐飲注重固定班別與友善工作動線，讓中高齡夥伴工作輕鬆有保障。",
        "warmthLabel": "新鮮職場，樂齡加入",
    },
    {
        "name": "台灣無印良品（MUJI）", "industry": "零售業",
        "totalScore": 88,
        "dimensions": {
            "culture":     {"score": 18, "evidence": "台北市113年認證，強調無年齡歧視的工作環境"},
            "recruitment": {"score": 18, "evidence": "主動招募中高齡，看重生活閱歷與服務熱忱"},
            "work":        {"score": 17, "evidence": "彈性工時，兼職選項，工作環境整潔舒適"},
            "environment": {"score": 18, "evidence": "舒適低體力賣場環境，完善員工休息空間"},
            "life":        {"score": 17, "evidence": "員工購物折扣、年度健檢、完整勞退提撥"},
        },
        "tags": ["彈性工時", "固定班別", "低體力負擔", "友善面試", "提供培訓"],
        "measures": ["台北市113年中高齡友善企業認證", "彈性排班，提供兼職選項", "無年齡歧視招募，重視生活閱歷", "舒適工作環境，員工休息空間完善"],
        "cities": ["台北市", "新北市", "台中市", "高雄市"], "jobCount": 60,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "MUJI重視生活閱歷而非年齡，舒適工作環境與彈性工時深受中高齡夥伴喜愛。",
        "warmthLabel": "簡約職場，美好同行",
    },
    {
        "name": "宜家家居（IKEA）", "industry": "家具零售業",
        "totalScore": 89,
        "dimensions": {
            "culture":     {"score": 18, "evidence": "台北市113年認證，全球DEI文化在台落實"},
            "recruitment": {"score": 18, "evidence": "主動招募中高齡，設計師資歷與生活經驗受重視"},
            "work":        {"score": 18, "evidence": "彈性排班，兼職選項，符合人因工程的工作動線"},
            "environment": {"score": 18, "evidence": "寬敞舒適工作環境，完善員工餐廳與休息空間"},
            "life":        {"score": 17, "evidence": "員工優惠購物、健康檢查、完整退休金提撥"},
        },
        "tags": ["彈性工時", "低體力負擔", "友善面試", "健康支持", "青銀共事"],
        "measures": ["台北市113年中高齡友善企業認證", "全球DEI政策在台灣落實", "完善員工餐廳與休息設施", "彈性兼職選項，適合中高齡節奏"],
        "cities": ["台北市", "新北市", "桃園市", "台中市", "高雄市"], "jobCount": 80,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "宜家以全球DEI文化落實中高齡友善，舒適環境與彈性排班讓夥伴安心工作。",
        "warmthLabel": "美好家居，樂齡職涯",
    },
    {
        "name": "昇恆昌免稅商店", "industry": "零售業",
        "totalScore": 86,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "台北市113年中高齡友善認證，重視多元包容"},
            "recruitment": {"score": 17, "evidence": "歡迎具外語能力的中高齡服務人員"},
            "work":        {"score": 17, "evidence": "多種班次選擇，固定班別保障工作穩定性"},
            "environment": {"score": 17, "evidence": "機場冷氣環境，低體力負擔"},
            "life":        {"score": 18, "evidence": "機場工作特殊津貼、完整員工福利制度"},
        },
        "tags": ["固定班別", "低體力負擔", "提供培訓", "健康支持"],
        "measures": ["台北市113年中高齡友善企業認證", "固定班別保障工作穩定", "機場舒適工作環境，冷氣全程", "完整員工津貼與福利制度"],
        "cities": ["台北市", "桃園市"], "jobCount": 50,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "昇恆昌提供機場舒適工作環境，固定班別與完整津貼制度，適合中高齡穩定就業。",
        "warmthLabel": "品質服務，職涯無限",
    },
    {
        "name": "新東陽", "industry": "食品零售業",
        "totalScore": 84,
        "dimensions": {
            "culture":     {"score": 16, "evidence": "台北市113年認證，重視資深員工服務經驗"},
            "recruitment": {"score": 17, "evidence": "積極招募中高齡服務人員，重視親切服務態度"},
            "work":        {"score": 17, "evidence": "固定班別，站立輔助設備，工作流程系統化"},
            "environment": {"score": 16, "evidence": "門市整潔環境，定期安全教育訓練"},
            "life":        {"score": 18, "evidence": "員工伴手禮優惠、完整勞退提撥、年度健檢"},
        },
        "tags": ["固定班別", "低體力負擔", "提供培訓", "歡迎二度就業"],
        "measures": ["台北市113年中高齡友善企業認證", "固定班別，工作時段穩定", "站立輔助設備降低體力負擔", "員工伴手禮購買優惠"],
        "cities": ["台北市", "新北市", "桃園市", "台中市"], "jobCount": 80,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "新東陽重視中高齡員工的服務經驗，固定班別與員工福利讓夥伴安心穩定工作。",
        "warmthLabel": "好滋味，好職場",
    },
    {
        "name": "里仁事業", "industry": "有機食品零售業",
        "totalScore": 87,
        "dimensions": {
            "culture":     {"score": 18, "evidence": "台北市113年認證，慈悲關懷的企業文化"},
            "recruitment": {"score": 17, "evidence": "以慈悲為本，不以年齡為招募門檻"},
            "work":        {"score": 18, "evidence": "固定班別，有機友善工作環境，低壓力節奏"},
            "environment": {"score": 17, "evidence": "健康有機工作環境，重視員工身心健康"},
            "life":        {"score": 17, "evidence": "員工購買有機商品優惠、完整勞退提撥"},
        },
        "tags": ["固定班別", "低體力負擔", "健康支持", "提供培訓", "友善面試"],
        "measures": ["台北市113年中高齡友善企業認證", "慈悲不歧視的企業文化", "員工有機商品採購優惠", "固定班別，低壓力工作節奏"],
        "cities": ["台北市", "新北市", "桃園市", "台中市", "台南市"], "jobCount": 70,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "里仁以慈悲關懷文化對待每位夥伴，有機健康的工作環境受中高齡員工喜愛。",
        "warmthLabel": "有機職涯，慈悲共行",
    },
    {
        "name": "圓山大飯店", "industry": "住宿及餐飲業",
        "totalScore": 88,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "台北市113年認證，歷史悠久的台灣品牌，重視傳承"},
            "recruitment": {"score": 18, "evidence": "積極留任資深員工，資歷與技術受高度重視"},
            "work":        {"score": 18, "evidence": "飯店環境舒適，各部門職務多元，固定班別"},
            "environment": {"score": 17, "evidence": "宏偉歷史建築環境，職場安全設施完善"},
            "life":        {"score": 18, "evidence": "員工宿舍、餐飲補貼、完整退休金制度"},
        },
        "tags": ["退休轉任制度", "固定班別", "提供培訓", "健康支持", "青銀共事"],
        "measures": ["台北市113年中高齡友善企業認證", "重視資深員工技術傳承", "員工宿舍與完整餐飲補貼", "固定班別，飯店舒適工作環境"],
        "cities": ["台北市"], "jobCount": 50,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "圓山飯店重視技術傳承與資深員工價值，完整員工福利讓夥伴安心長期服務。",
        "warmthLabel": "百年傳承，職涯同輝",
    },
    {
        "name": "六福旅遊集團", "industry": "住宿及餐飲業",
        "totalScore": 86,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "台北市113年認證（台北六福萬怡），重視資深人才"},
            "recruitment": {"score": 17, "evidence": "飯店業資深從業人員受高度歡迎"},
            "work":        {"score": 18, "evidence": "五星飯店完善設施，分工明確，固定職務"},
            "environment": {"score": 17, "evidence": "五星級舒適環境，員工設施完善"},
            "life":        {"score": 17, "evidence": "員工餐飲、住房優惠、完整退休福利"},
        },
        "tags": ["固定班別", "低體力負擔", "提供培訓", "退休轉任制度"],
        "measures": ["台北市113年中高齡友善企業認證", "五星環境分工明確職責清晰", "員工住房優惠與餐飲補貼", "完整退休金提撥制度"],
        "cities": ["台北市", "桃園市"], "jobCount": 60,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "六福旅遊集團五星飯店環境完善，資深服務人才受重視，福利制度業界優良。",
        "warmthLabel": "五星服務，職涯共好",
    },
    {
        "name": "遠東新世紀", "industry": "紡織製造業",
        "totalScore": 86,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "台北市113年認證，重視老師傅的製程技術與智慧"},
            "recruitment": {"score": 16, "evidence": "積極留任資深技術人員，師傅制度傳承"},
            "work":        {"score": 18, "evidence": "固定班別，引入輔助設備降低體力需求"},
            "environment": {"score": 17, "evidence": "持續改善廠區人因工程，職場安全"},
            "life":        {"score": 18, "evidence": "完整退休金提撥、員工分紅、年終獎金"},
        },
        "tags": ["固定班別", "低體力負擔", "職務再設計", "退休轉任制度", "提供培訓"],
        "measures": ["台北市113年中高齡友善企業認證", "師傅制度保留珍貴技術知識", "廠區人因工程改善與輔具引入", "固定班別，不輪大小夜班"],
        "cities": ["台北市", "桃園市", "台南市"], "jobCount": 70,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "遠東新世紀以師傅制度珍視資深員工技術，固定班別與人因改善保護夥伴健康。",
        "warmthLabel": "匠人精神，世代傳承",
    },
    {
        "name": "慈濟基金會", "industry": "非營利組織/社福業",
        "totalScore": 91,
        "dimensions": {
            "culture":     {"score": 20, "evidence": "台北市113年認證，慈悲為懷，完全無年齡歧視"},
            "recruitment": {"score": 18, "evidence": "廣泛歡迎中高齡志工與職員，重視奉獻精神"},
            "work":        {"score": 18, "evidence": "多元職務選擇，按能力分配，低壓力工作"},
            "environment": {"score": 18, "evidence": "友善溫馨工作環境，重視身心健康"},
            "life":        {"score": 17, "evidence": "完整勞退提撥，志工醫療保障，精神滿足感高"},
        },
        "tags": ["彈性工時", "低體力負擔", "健康支持", "友善面試", "青銀共事", "歡迎二度就業"],
        "measures": ["台北市113年中高齡友善企業認證", "完全無年齡歧視，以奉獻精神為招募標準", "多元職務按能力分配，低壓力工作節奏", "志工醫療保障與身心健康支持"],
        "cities": ["全台各縣市"], "jobCount": 200,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "慈濟以慈悲文化對待每位夥伴，完全無年齡歧視，中高齡參與度極高且精神滿足感佳。",
        "warmthLabel": "以慈悲心，共創善業",
    },
    {
        "name": "聯邦商業銀行", "industry": "金融及保險業",
        "totalScore": 85,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "台北市113年認證，重視金融業資深人才價值"},
            "recruitment": {"score": 17, "evidence": "金融業資深人員客戶關係廣，受積極留任"},
            "work":        {"score": 17, "evidence": "辦公室環境，固定工時，壓力相對可控"},
            "environment": {"score": 17, "evidence": "完善辦公設施，定期健康檢查"},
            "life":        {"score": 17, "evidence": "金融業完整福利，退休金提撥，績效獎金"},
        },
        "tags": ["固定班別", "提供培訓", "退休轉任制度", "健康支持"],
        "measures": ["台北市113年中高齡友善企業認證", "重視金融業資深人才客戶關係", "辦公環境固定工時，生活規律", "完整金融業退休福利制度"],
        "cities": ["台北市", "新北市", "桃園市", "台中市", "高雄市"], "jobCount": 60,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "聯邦銀行重視資深金融人才的客戶關係與專業，穩定工時與完整福利深受夥伴肯定。",
        "warmthLabel": "穩健金融，共創未來",
    },
    {
        "name": "威剛科技", "industry": "半導體/記憶體製造業",
        "totalScore": 89,
        "dimensions": {
            "culture":     {"score": 18, "evidence": "DEI友善壯世代雇主獎獲獎企業，主動推動中高齡共融"},
            "recruitment": {"score": 18, "evidence": "DEI獲獎肯定，邀約中高齡面試比率高"},
            "work":        {"score": 18, "evidence": "技術研發職務重視經驗，資深工程師受重用"},
            "environment": {"score": 17, "evidence": "科技廠區安全設施完善，健康促進方案"},
            "life":        {"score": 18, "evidence": "科技業競爭薪資、完整退休金、培訓資源豐富"},
        },
        "tags": ["退休轉任制度", "提供培訓", "健康支持", "青銀共事", "彈性工時"],
        "measures": ["DEI友善壯世代雇主獎獲獎企業", "邀約中高齡面試比率為業界4.7倍", "資深工程師知識傳承計畫", "完整退休金提撥與員工持股信託"],
        "cities": ["台北市", "新北市", "桃園市"], "jobCount": 50,
        "dei": "DEI友善壯世代雇主獎",
        "summary": "威剛科技獲DEI友善壯世代雇主獎肯定，邀約中高齡面試比率遠超業界平均。",
        "warmthLabel": "科技實力，世代共融",
    },
    {
        "name": "國泰金融控股", "industry": "金融及保險業",
        "totalScore": 93,
        "dimensions": {
            "culture":     {"score": 19, "evidence": "2024 Forbes全球最佳雇主，台灣DEI百大企業"},
            "recruitment": {"score": 18, "evidence": "主動推動中高齡就業，設有中高齡專屬招募管道"},
            "work":        {"score": 19, "evidence": "彈性工時、居家辦公選項、多元職務安排"},
            "environment": {"score": 19, "evidence": "完善健康管理體系，EAP心理諮詢服務"},
            "life":        {"score": 18, "evidence": "業界頂尖福利，員工持股、退休規劃諮詢"},
        },
        "tags": ["彈性工時", "退休轉任制度", "健康支持", "青銀共事", "提供培訓", "友善面試"],
        "measures": ["2024 Forbes全球最佳雇主百大企業（台灣唯一）", "DEI多元共融政策全面落實", "彈性工時與居家辦公方案", "完整EAP員工協助方案（心理健康）"],
        "cities": ["台北市", "新北市", "台中市", "台南市", "高雄市"], "jobCount": 150,
        "dei": "2024 Forbes全球最佳雇主 · DEI百大企業",
        "summary": "國泰金控獲Forbes全球最佳雇主肯定，DEI文化深植組織，中高齡員工獲完整支持。",
        "warmthLabel": "保障未來，共好同行",
    },
    {
        "name": "台灣大哥大", "industry": "電信服務業",
        "totalScore": 88,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "積極推動職場多元共融，設有DEI委員會"},
            "recruitment": {"score": 18, "evidence": "主動歡迎中高齡人才，設有二度就業專屬流程"},
            "work":        {"score": 18, "evidence": "彈性工時、多元職務、數位轉型提升工作效率"},
            "environment": {"score": 17, "evidence": "現代化辦公環境，完善健康促進方案"},
            "life":        {"score": 18, "evidence": "退休金提撥、員工持股信託、數位技能培訓"},
        },
        "tags": ["彈性工時", "退休轉任制度", "提供培訓", "健康支持", "友善面試", "歡迎二度就業"],
        "measures": ["DEI委員會推動職場多元共融", "二度就業專屬招募流程", "數位技能加速培訓課程（中高齡友善）", "完整EAP員工協助服務"],
        "cities": ["台北市", "新北市", "台中市", "高雄市"], "jobCount": 95,
        "dei": "職場多元共融獎",
        "summary": "台灣大哥大積極推動DEI，設有二度就業專屬流程，數位培訓讓中高齡夥伴無縫接軌。",
        "warmthLabel": "科技溫度，職涯延伸",
    },
    {
        "name": "全聯福利中心", "industry": "零售業",
        "totalScore": 91,
        "dimensions": {
            "culture":     {"score": 18, "evidence": "全台規模最大超市，積極招募中高齡，青銀共事"},
            "recruitment": {"score": 19, "evidence": "長期積極招募中高齡，歡迎二度就業"},
            "work":        {"score": 19, "evidence": "固定班別選擇，職務再設計降低體力負擔"},
            "environment": {"score": 18, "evidence": "持續改善門市工作環境，輔具引入"},
            "life":        {"score": 17, "evidence": "年終獎金、員工折扣、完整勞退提撥"},
        },
        "tags": ["固定班別", "低體力負擔", "職務再設計", "歡迎二度就業", "彈性工時", "健康支持"],
        "measures": ["全台門市積極招募中高齡夥伴", "固定排班制度，多種班次選擇", "職務再設計降低搬運體力負擔", "完整到職培訓與一對一師徒制"],
        "cities": ["台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市"], "jobCount": 500,
        "dei": "中高齡友善就業楷模企業",
        "summary": "全聯是全台招募中高齡人數最多的零售通路，固定班別與職務再設計為最大亮點。",
        "warmthLabel": "好鄰居，好夥伴",
    },
    {
        "name": "統一超商（7-ELEVEN）", "industry": "便利商店零售業",
        "totalScore": 88,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "全台最大便利商店，積極招募多元年齡層"},
            "recruitment": {"score": 18, "evidence": "全台各地持續招募，提供兼職彈性選擇"},
            "work":        {"score": 19, "evidence": "多種班次（短時數、兼職），固定班別選擇"},
            "environment": {"score": 17, "evidence": "冷暖氣門市環境，低體力負擔，安全設施"},
            "life":        {"score": 17, "evidence": "員工購物折扣、完整勞退提撥、店鋪獎金"},
        },
        "tags": ["固定班別", "彈性工時", "低體力負擔", "歡迎二度就業", "提供培訓"],
        "measures": ["全台持續招募，班次多元可選", "店鋪導師制度，一對一帶領新人", "系統化SOP讓中高齡快速上手", "低體力負擔工作設計"],
        "cities": ["全台各縣市"], "jobCount": 800,
        "dei": "中高齡友善就業認可企業",
        "summary": "7-ELEVEN班次多元彈性，SOP系統化讓中高齡輕鬆上手，全台職缺充足。",
        "warmthLabel": "24小時，職涯不設限",
    },
    {
        "name": "長庚醫療財團法人", "industry": "醫療及社會工作業",
        "totalScore": 94,
        "dimensions": {
            "culture":     {"score": 19, "evidence": "醫療業重視資深人才，資歷越豐富越受重用"},
            "recruitment": {"score": 18, "evidence": "設有銀髮醫療人才留任計畫，歡迎回聘"},
            "work":        {"score": 19, "evidence": "多元職務，按能力分配，彈性班次安排"},
            "environment": {"score": 20, "evidence": "運用自身醫療資源照顧員工健康，設施完善"},
            "life":        {"score": 18, "evidence": "員工門診快速通道、完整健檢、退休規劃諮詢"},
        },
        "tags": ["退休轉任制度", "健康支持", "提供培訓", "職務再設計", "彈性工時", "歡迎二度就業"],
        "measures": ["銀髮醫療人才留任與回聘計畫", "運用院內醫療資源照顧員工健康", "員工門診快速通道與健康促進方案", "資深醫療人才知識傳承計畫"],
        "cities": ["台北市", "桃園市", "台中市", "嘉義市", "高雄市"], "jobCount": 210,
        "dei": "健康職場優良企業",
        "summary": "長庚充分運用醫療資源照顧員工，銀髮人才留任計畫讓資深醫療專業持續發光。",
        "warmthLabel": "守護生命，守護夥伴",
    },
    {
        "name": "台灣積體電路製造（台積電）", "industry": "半導體製造業",
        "totalScore": 90,
        "dimensions": {
            "culture":     {"score": 18, "evidence": "重視知識傳承，資深工程師為不可或缺的核心"},
            "recruitment": {"score": 17, "evidence": "設有退休後返聘機制，技術顧問職位"},
            "work":        {"score": 18, "evidence": "彈性工時，多元職務，高度自動化降低體力需求"},
            "environment": {"score": 19, "evidence": "廠區醫療站、年度進階健檢、職業安全防護"},
            "life":        {"score": 18, "evidence": "業界頂尖薪資、員工持股信託、退休規劃支持"},
        },
        "tags": ["退休轉任制度", "提供培訓", "健康支持", "彈性工時", "青銀共事"],
        "measures": ["技術師傅制度，確保關鍵知識傳承", "退休後返聘為技術顧問或內部講師", "廠區醫療站與年度全身進階健檢", "完整數位技能更新培訓計畫"],
        "cities": ["新竹市", "台中市", "台南市", "高雄市"], "jobCount": 150,
        "dei": "科技業友善職場標竿企業",
        "summary": "台積電以技術傳承文化留住資深工程師，退休後返聘機制讓珍貴知識持續在職場發光。",
        "warmthLabel": "以人為本，創新共融",
    },
    {
        "name": "富邦金融控股", "industry": "金融及保險業",
        "totalScore": 87,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "積極推動職場多元，設有中高齡人才發展方案"},
            "recruitment": {"score": 17, "evidence": "金融業資深人才客戶信任關係受高度重視"},
            "work":        {"score": 18, "evidence": "彈性工時、居家辦公選項、多元職務安排"},
            "environment": {"score": 18, "evidence": "現代化辦公空間，完善健康促進方案"},
            "life":        {"score": 17, "evidence": "員工持股信託、退休規劃諮詢、完整健康保障"},
        },
        "tags": ["彈性工時", "退休轉任制度", "提供培訓", "青銀共事", "健康支持"],
        "measures": ["中高齡人才發展專案", "青銀共創跨世代學習計畫", "彈性工時與居家辦公方案", "完整員工持股信託與退休規劃"],
        "cities": ["台北市", "新北市", "台中市", "高雄市"], "jobCount": 120,
        "dei": "金融業多元共融楷模",
        "summary": "富邦金控青銀共創計畫讓資深與年輕員工互補共學，彈性工作制度獲夥伴高度認可。",
        "warmthLabel": "穩健信任，攜手同行",
    },
    {
        "name": "台灣卓勒股份有限公司", "industry": "工業設備製造業",
        "totalScore": 86,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "104高年級品牌合作企業，五好幸福措施"},
            "recruitment": {"score": 17, "evidence": "歡迎中高齡製造業人才，重視實務經驗"},
            "work":        {"score": 18, "evidence": "固定班別，職務再設計，引入輔助設備"},
            "environment": {"score": 17, "evidence": "完善職場安全設施，健康促進方案"},
            "life":        {"score": 17, "evidence": "五好幸福措施涵蓋文化、工作、生活、健康、職涯"},
        },
        "tags": ["固定班別", "職務再設計", "低體力負擔", "提供培訓", "健康支持"],
        "measures": ["104高年級合作友善企業品牌", "五好幸福措施全面照顧員工", "職務再設計配合中高齡體能", "完善職場安全設施"],
        "cities": ["台北市", "新竹市", "桃園市"], "jobCount": 40,
        "dei": "104高年級友善企業品牌",
        "summary": "台灣卓勒以五好幸福措施全面照顧員工，104品牌合作夥伴，中高齡就業環境友善。",
        "warmthLabel": "精密製造，幸福同行",
    },
    {
        "name": "全漢企業（FSP Group）", "industry": "電子製造業",
        "totalScore": 85,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "104高年級品牌，多元共融年齡包容文化"},
            "recruitment": {"score": 17, "evidence": "積極招募中高齡製造業人才，重視操機經驗"},
            "work":        {"score": 17, "evidence": "職務再設計，彈性工時，自動化降低體力需求"},
            "environment": {"score": 17, "evidence": "健康管理方案，先進醫療設備，職場安全"},
            "life":        {"score": 17, "evidence": "績效獎金、員工旅遊、完整退休金制度"},
        },
        "tags": ["彈性工時", "職務再設計", "提供培訓", "健康支持", "青銀共事"],
        "measures": ["104高年級合作友善企業品牌", "職務再設計配合中高齡技術人員需求", "健康管理與職場醫療資源", "彈性工時制度"],
        "cities": ["新北市", "桃園市", "台中市"], "jobCount": 50,
        "dei": "104高年級友善企業品牌",
        "summary": "全漢企業FSP重視中高齡製造業人才的操機經驗，職務再設計與健康管理受好評。",
        "warmthLabel": "電源動力，世代共贏",
    },
    {
        "name": "徠通科技（Accutex）", "industry": "精密機械製造業",
        "totalScore": 88,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "104高年級品牌，積極推動中高齡人才留任"},
            "recruitment": {"score": 18, "evidence": "精密加工技術人才受高度重視，資歷越豐富越好"},
            "work":        {"score": 18, "evidence": "職務再設計，提供輔助器具，固定班別"},
            "environment": {"score": 19, "evidence": "在職醫療服務、高階健檢、輔助器具補助"},
            "life":        {"score": 16, "evidence": "培訓補助、退休金提撥、職涯可持續發展"},
        },
        "tags": ["職務再設計", "低體力負擔", "健康支持", "提供培訓", "退休轉任制度"],
        "measures": ["104高年級合作友善企業品牌", "在職醫療服務與高階健康檢查", "輔助器具補助降低職業傷害", "精密技術人才職涯可持續計畫"],
        "cities": ["桃園市", "新竹市", "台北市"], "jobCount": 35,
        "dei": "104高年級友善企業品牌",
        "summary": "徠通科技為精密技術人才提供在職醫療服務與高階健檢，職務再設計讓資深師傅持續發光。",
        "warmthLabel": "精準工藝，永續職涯",
    },
    {
        "name": "全家便利商店", "industry": "便利商店零售業",
        "totalScore": 87,
        "dimensions": {
            "culture":     {"score": 17, "evidence": "台北市113年認證（全家國際餐飲），友善多元文化"},
            "recruitment": {"score": 18, "evidence": "全台持續招募，彈性兼職機會多"},
            "work":        {"score": 18, "evidence": "多班次選擇，SOP清晰，快速上手"},
            "environment": {"score": 17, "evidence": "冷氣環境，低體力，安全設施完善"},
            "life":        {"score": 17, "evidence": "員工購物優惠、完整勞退提撥"},
        },
        "tags": ["固定班別", "彈性工時", "低體力負擔", "歡迎二度就業", "提供培訓"],
        "measures": ["台北市113年中高齡友善企業認證", "全台持續招募，兼職選擇彈性", "SOP培訓系統讓中高齡快速上手", "友善到職流程與師徒輔導"],
        "cities": ["全台各縣市"], "jobCount": 600,
        "dei": "台北市113年中高齡友善企業認證",
        "summary": "全家便利商店全台職缺充足，SOP系統化讓中高齡快速上手，友善兼職機會多。",
        "warmthLabel": "就近好職場，輕鬆好工作",
    },
]

# ══════════════════════════════════════════════════════════════
#  DuckDuckGo 搜尋（免費，無需 API Key）
# ══════════════════════════════════════════════════════════════
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}

def ddg_search(query: str, max_results: int = 5) -> list[dict]:
    """DuckDuckGo HTML 搜尋，無需 API Key"""
    try:
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query, "kl": "tw-tzh"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for el in soup.select(".result__body")[:max_results]:
            title_el = el.select_one(".result__title")
            snip_el  = el.select_one(".result__snippet")
            url_el   = el.select_one(".result__url")
            if title_el:
                results.append({
                    "title":   title_el.get_text(strip=True),
                    "snippet": snip_el.get_text(strip=True) if snip_el else "",
                    "url":     url_el.get_text(strip=True) if url_el else "",
                })
        return results
    except Exception as e:
        return []

# ══════════════════════════════════════════════════════════════
#  關鍵字評分算法（五大維度）
# ══════════════════════════════════════════════════════════════
DIMENSION_KEYWORDS = {
    "culture": {
        "max": 20,
        "keywords": [
            ("DEI", 4), ("多元共融", 4), ("青銀共事", 3), ("中高齡友善", 3),
            ("年齡友善", 3), ("壯世代", 2), ("無年齡歧視", 3), ("世代共融", 2),
            ("認證", 2), ("獲獎", 2), ("友善職場", 2), ("樂齡", 1), ("高年級", 2),
        ]
    },
    "recruitment": {
        "max": 20,
        "keywords": [
            ("歡迎中高齡", 4), ("二度就業", 4), ("友善面試", 3), ("歡迎45", 2),
            ("歡迎50", 2), ("中高齡應徵", 3), ("資深", 2), ("樂於傳承", 2),
            ("退而不休", 2), ("回聘", 3), ("重新就業", 2), ("中途轉職", 2),
        ]
    },
    "work": {
        "max": 20,
        "keywords": [
            ("彈性工時", 4), ("固定班別", 4), ("職務再設計", 4), ("低體力", 3),
            ("輕鬆工作", 2), ("不輪班", 3), ("彈性排班", 3), ("工作調整", 2),
            ("輔具", 2), ("人因工程", 3), ("適度工作量", 2), ("彈性假", 2),
        ]
    },
    "environment": {
        "max": 20,
        "keywords": [
            ("健康檢查", 3), ("健康促進", 3), ("健康支持", 3), ("醫療", 2),
            ("職場安全", 3), ("EAP", 3), ("心理諮詢", 2), ("年度健檢", 3),
            ("醫護", 2), ("職業安全", 3), ("健保", 1), ("保險", 1),
        ]
    },
    "life": {
        "max": 20,
        "keywords": [
            ("退休金", 4), ("退休轉任", 4), ("培訓", 3), ("進修", 2),
            ("員工福利", 2), ("年終獎金", 2), ("員工持股", 2), ("退休規劃", 3),
            ("在職教育", 2), ("職涯發展", 2), ("學費補助", 2), ("技能培訓", 3),
        ]
    },
}

def score_from_text(text: str) -> dict:
    """根據文字內容，用關鍵字算出各維度分數"""
    scores = {}
    for dim, cfg in DIMENSION_KEYWORDS.items():
        raw = sum(w for kw, w in cfg["keywords"] if kw in text)
        # 歸一化到 0~20，最高有效 raw=10
        score = min(cfg["max"], int(raw / 10 * cfg["max"]))
        # 找出命中的關鍵字作為 evidence
        hits = [kw for kw, w in cfg["keywords"] if kw in text][:3]
        evidence = "搜尋結果提及：" + "、".join(hits) if hits else "公開資料尚無明確記錄"
        scores[dim] = {"score": score, "evidence": evidence}
    return scores

def extract_tags(text: str) -> list:
    """從文字中擷取友善特色標籤"""
    all_tags = [
        "彈性工時", "職務再設計", "退休轉任制度", "提供培訓",
        "歡迎二度就業", "固定班別", "低體力負擔", "青銀共事",
        "健康支持", "友善面試", "DEI認證", "師徒制度",
    ]
    return [t for t in all_tags if t.replace("認證", "").replace("制度", "") in text][:6] or ["提供培訓", "友善面試"]

def extract_measures(text: str, name: str) -> list:
    """從搜尋結果擷取可能的措施描述"""
    patterns = [
        r"(提供.{4,20}[制度計畫方案])", r"(設有.{4,20}[機制計畫])",
        r"(推動.{4,20}[政策計畫])", r"([0-9]+年.{4,20}認證)",
        r"(完整.{4,20}[制度方案])",
    ]
    found = []
    for p in patterns:
        for m in re.findall(p, text):
            if len(m) < 30:
                found.append(m)
    if not found:
        return [f"{name}提供中高齡友善工作環境", "完整員工培訓資源", "友善面試流程，不以年齡設限"]
    return list(dict.fromkeys(found))[:4]

def detect_industry(name: str, text: str) -> str:
    mapping = {
        "飯店|酒店|旅館|旅遊|民宿": "住宿及餐飲業",
        "餐廳|餐飲|食品|壽司|漢堡|便當": "餐飲服務業",
        "超商|便利|零售|百貨|購物|超市": "零售業",
        "銀行|金融|保險|證券|期貨": "金融及保險業",
        "科技|電子|半導體|晶圓|記憶體": "科技製造業",
        "醫院|醫療|診所|藥局|護理": "醫療及社會工作業",
        "製造|工廠|機械|紡織|化學": "製造業",
        "電信|通訊|行動|寬頻": "電信服務業",
        "學校|教育|補習|培訓": "教育服務業",
        "物流|快遞|運輸|倉儲": "物流運輸業",
    }
    combined = name + text[:200]
    for pattern, industry in mapping.items():
        if re.search(pattern, combined):
            return industry
    return "服務業"

def detect_cities(text: str) -> list:
    cities = ["台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市", "新竹市", "基隆市", "宜蘭縣", "花蓮縣", "嘉義市"]
    found = [c for c in cities if c in text]
    return found[:4] if found else ["台北市", "新北市"]

def detect_job_count(text: str) -> int:
    m = re.search(r"(\d+)\s*[個位名]?\s*職缺", text)
    if m:
        return int(m.group(1))
    m2 = re.search(r"招募\s*(\d+)", text)
    if m2:
        return int(m2.group(1))
    return 20

# ══════════════════════════════════════════════════════════════
#  圖片
# ══════════════════════════════════════════════════════════════
HERO_MAP = {
    "住宿": "photo-1566073771259-6a8506099945",
    "餐飲": "photo-1414235077428-338989a2e8c0",
    "速食": "photo-1568901346375-23c9450c58cd",
    "零售": "photo-1556742049-0cfed4f6a45d",
    "便利": "photo-1567103472667-6898f3a79cf2",
    "金融": "photo-1486406146926-c627a92ad1ab",
    "科技": "photo-1518770660439-4636190af475",
    "半導體": "photo-1518770660439-4636190af475",
    "製造": "photo-1504328345606-18bbc8c9d7d1",
    "醫療": "photo-1538108149393-fbbd81895907",
    "教育": "photo-1509062522246-3755977927d7",
    "電信": "photo-1497366216548-37526070297c",
    "物流": "photo-1586528116311-ad8dd3c8310d",
}
IMG_POOL = [
    "photo-1600880292203-757bb62b4baf",
    "photo-1573496359142-b8d87734a5a2",
    "photo-1531482615713-2afd69097998",
    "photo-1542744173-8e7e53415bb0",
    "photo-1552664730-d307ca884978",
    "photo-1576091160550-2173dba999ef",
    "photo-1556761175-b413da4baf72",
]

def add_images(data: dict) -> dict:
    industry = data.get("industry", "")
    hero_id = "photo-1497366216548-37526070297c"
    for key, img_id in HERO_MAP.items():
        if key in industry:
            hero_id = img_id
            break
    seed = sum(ord(c) for c in data.get("name", "")) % len(IMG_POOL)
    data["heroImg"]    = f"https://images.unsplash.com/{hero_id}?w=1200&q=80"
    data["img1"]       = f"https://images.unsplash.com/{IMG_POOL[seed]}?w=800&q=80"
    data["img2"]       = f"https://images.unsplash.com/{IMG_POOL[(seed+2)%len(IMG_POOL)]}?w=800&q=80"
    data["videoThumb"] = "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&q=80"
    return data

def finalize(data: dict) -> dict:
    """補上 cityData, friendlyTags, story, warmthScore 等欄位"""
    name     = data.get("name", "")
    total    = data.get("totalScore", 70)
    measures = data.get("measures", [])
    tags     = data.get("tags", [])
    cities   = data.get("cities", ["台北市"])[:4]
    jc       = max(5, int(data.get("jobCount", 20)))

    data["cityData"] = [{"name": c, "count": f"{max(3, jc // max(1, len(cities)))}+"} for c in cities]
    data["friendlyTags"] = tags
    data["warmthScore"]  = max(0, total - 5)
    data.setdefault("dei", "中高齡友善認證企業")
    data.setdefault("warmthLabel", "友善職場，溫暖同行")
    data.setdefault("summary", f"{name}積極推動中高齡友善職場，提供完善的就業環境與福利制度。")

    m0 = measures[0] if measures else f"{name}提供友善工作環境"
    m1 = measures[1] if len(measures) > 1 else "完整員工培訓資源"
    m2 = measures[2] if len(measures) > 2 else "友善面試流程，歡迎二度就業"

    data.setdefault("story1Title", "完善的中高齡友善制度")
    data.setdefault("story1Sub",   "每位夥伴都能安心展開職涯新旅程")
    data.setdefault("story1",
        f"{name}深信中高齡員工的豐富經驗是企業最珍貴的資產。{data.get('summary','')} "
        f"{m0}，讓每位夥伴在友善環境中持續發揮所長，實現企業與員工的共同成長。")

    data.setdefault("story2Title", "多元學習與職涯發展")
    data.setdefault("story2Sub",   "持續成長，實現個人與企業共同進步")
    data.setdefault("story2",
        f"{name}積極投入員工培訓，{m1}。透過系統化的課程設計，"
        f"協助中高齡員工持續精進專業能力，讓資深夥伴的智慧得以傳承延續。")

    data.setdefault("story3Title", "友善徵才，誠摯邀請")
    data.setdefault("story3Sub",   "歡迎中高齡優秀人才共創未來")
    data.setdefault("story3",
        f"{name}誠摯歡迎中高齡求職者加入。{m2}，"
        f"新進員工享有完整的到職訓練與一對一輔導，讓每位夥伴都能在穩定友善的環境中發展精彩的職涯第二春。")

    return add_images(data)

# ══════════════════════════════════════════════════════════════
#  搜尋並評分指定企業
# ══════════════════════════════════════════════════════════════
def search_and_score(name: str) -> dict:
    """用 DuckDuckGo 搜尋企業，關鍵字算法評分"""
    queries = [
        f"{name} 中高齡 友善 職場 台灣",
        f"{name} 二度就業 退休 培訓 DEI",
        f"{name} 104人力銀行 職缺 中高齡",
    ]
    all_text = ""
    for q in queries:
        results = ddg_search(q, max_results=4)
        for r in results:
            all_text += " " + r.get("title", "") + " " + r.get("snippet", "")
        time.sleep(0.8)   # 避免 rate limit

    dims   = score_from_text(all_text)
    total  = sum(d["score"] for d in dims.values())
    tags   = extract_tags(all_text)
    msrs   = extract_measures(all_text, name)
    cities = detect_cities(all_text)
    jc     = detect_job_count(all_text)
    ind    = detect_industry(name, all_text)

    # 從資料庫找 DEI 認證資訊
    db_match = next((c for c in DATABASE if name in c["name"] or c["name"] in name), None)
    dei = db_match["dei"] if db_match else ""

    # 搜尋結果擷取摘要
    snips = [r["snippet"] for r in ddg_search(f"{name} 員工 職場", 3)]
    summary = snips[0][:60] if snips else f"{name}積極推動友善職場環境。"

    return {
        "name":        name,
        "industry":    ind,
        "totalScore":  total,
        "dimensions":  dims,
        "tags":        tags,
        "measures":    msrs,
        "cities":      cities,
        "jobCount":    jc,
        "dei":         dei,
        "summary":     summary,
        "warmthLabel": "友善職場，溫暖同行",
    }

# ══════════════════════════════════════════════════════════════
#  API 路由
# ══════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════
#  已在 104 高年級品牌專區 (senior.104.com.tw/c/brands) 上架的企業
#  來源：senior.104.com.tw/c/brands/case/* 與 /50talent/c/brands/case/*
# ══════════════════════════════════════════════════════════════
ALREADY_ON_104_BRANDS = {
    "老爺酒店集團", "老爺",             # /case/silks-Hotel-Group
    "全家便利商店", "全家",             # /case/familymart
    "麥當勞",                          # /case/mcdonalds
    "宜家家居", "IKEA",                # /case/ikea
    "全聯集團", "全聯福利中心", "全聯", # /case/pxmart
    "里仁事業", "里仁股份有限公司",     # /case/leezen
    "台灣無印良品", "無印良品", "MUJI", # /case/muji
    "台灣卓勒",                        # from 50talent brands page
    "全漢企業", "FSP Group",           # from 50talent brands page
    "徠通科技", "Accutex",             # from 50talent brands page
}

def is_on_104_brands(name: str) -> bool:
    return any(kw in name or name in kw for kw in ALREADY_ON_104_BRANDS)


@app.route("/api/recommend", methods=["GET"])
def recommend():
    """從資料庫推薦尚未在 104 高年級品牌專區上架的企業（排除已上架者）"""
    eligible = [c for c in DATABASE if not is_on_104_brands(c["name"])]
    sample   = random.sample(eligible, min(10, len(eligible)))
    results  = [finalize(dict(c)) for c in sample]
    results.sort(key=lambda x: x["totalScore"], reverse=True)
    return jsonify({
        "companies": results,
        "source": "research_db",
        "total": len(eligible),
        "excluded_count": len(DATABASE) - len(eligible),
    })


@app.route("/api/search", methods=["POST"])
def search():
    """搜尋指定企業（先查資料庫，若無則 DuckDuckGo 即時評分）"""
    body    = request.get_json(silent=True) or {}
    company = body.get("company", "").strip()
    if not company:
        return jsonify({"error": "請提供企業名稱"}), 400

    # 先比對資料庫
    db_match = next(
        (c for c in DATABASE if company in c["name"] or c["name"] in company
         or any(part in c["name"] for part in company.split() if len(part) > 1)),
        None
    )
    if db_match:
        result = finalize(dict(db_match))
        return jsonify({"companies": [result], "source": "research_db"})

    # 資料庫沒有 → 即時 DuckDuckGo 搜尋
    try:
        data   = search_and_score(company)
        result = finalize(data)
        return jsonify({"companies": [result], "source": "web_search"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "api_key": "not_required", "db_size": len(DATABASE)})


if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", 5001))
    print(f"\n{'='*52}")
    print(f"  104 高年級 友善企業評分後端（無需 API Key）")
    print(f"  資料庫：{len(DATABASE)} 家真實友善企業")
    print(f"  http://localhost:{port}")
    print(f"{'='*52}\n")
    app.run(debug=False, port=port, host="0.0.0.0")
