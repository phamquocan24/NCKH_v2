# utils/text_processing.py
import re
import urllib.parse

def preprocess_for_spam_detection(text):
    """
    Tiền xử lý đặc biệt cho việc phát hiện spam
    """
    # Bản sao văn bản gốc để phân tích
    original_text = text
    
    # Xử lý các URL
    # Tìm tất cả các URL trong văn bản
    url_pattern = r'https?://\S+|www\.\S+|bit\.ly/\S+|goo\.gl/\S+|t\.co/\S+|tinyurl\.com/\S+'
    urls = re.findall(url_pattern, original_text)
    
    # Đánh dấu có URL
    has_url = len(urls) > 0
    
    # Đếm số lượng URL
    url_count = len(urls)
    
    # Kiểm tra các domain phổ biến trong spam
    suspicious_domains = ['bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'shorturl']
    has_suspicious_url = any(domain in url for url in urls for domain in suspicious_domains)
    
    # Xử lý các từ khóa spam tiếng Việt phổ biến
    spam_keywords = [
        'giảm giá', 'khuyến mãi', 'siêu sale', 'mua ngay', 'giá sốc', 'giá rẻ',
        'liên hệ ngay', 'số lượng có hạn', 'cơ hội cuối', 'miễn phí', 'làm giàu',
        'kiếm tiền tại nhà', 'thu nhập thụ động', 'việc làm thêm', 'đầu tư',
        'chiết khấu', 'sale off', 'freeship', 'mua 1 tặng 1'
    ]
    
    # Chuẩn hóa văn bản để kiểm tra từ khóa
    normalized_text = text.lower()
    # Loại bỏ các ký tự đặc biệt thường dùng để tránh bộ lọc
    normalized_text = re.sub(r'[._\-\s*]', '', normalized_text)
    
    # Đếm số từ khóa spam xuất hiện
    spam_keyword_count = sum(1 for keyword in spam_keywords if keyword.replace(' ', '') in normalized_text)
    
    # Kiểm tra các đặc điểm đặc trưng của spam
    has_excessive_punctuation = len(re.findall(r'[!?.]', text)) > 3
    has_all_caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text)) > 0
    
    # Tạo đặc trưng bổ sung cho mô hình
    spam_features = {
        'has_url': has_url,
        'url_count': url_count,
        'has_suspicious_url': has_suspicious_url,
        'spam_keyword_count': spam_keyword_count,
        'has_excessive_punctuation': has_excessive_punctuation,
        'has_all_caps_words': has_all_caps_words
    }
    
    return text, spam_features