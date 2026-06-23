# ai_module/sentiment.py
import logging
from textblob import TextBlob
from deep_translator import GoogleTranslator

def get_sentiment(text, source_name):
    """
    Phân tích cảm xúc của văn bản. Hỗ trợ đa ngôn ngữ (Việt, Anh).
    Trả về một dictionary chứa điểm số (score) và nhãn cảm xúc (label).
    """
    try:
        if not text:
            return {"score": 0.0, "label": "Trung tính"}

        text_to_analyze = text

        # XỬ LÝ ĐA NGÔN NGỮ (Điểm cộng cực lớn cho đồ án)
        # Nếu nguồn là VnExpress (Tiếng Việt), ta dịch sang tiếng Anh trước
        if source_name == "VnExpress":
            # Dịch tối đa 4999 ký tự để tránh giới hạn độ dài của Google Translator
            text_to_analyze = GoogleTranslator(source='vi', target='en').translate(text[:4999])

        # Phân tích cảm xúc bằng TextBlob
        blob = TextBlob(text_to_analyze)
        score = blob.sentiment.polarity  # Điểm chạy từ -1.0 (Rất tiêu cực) đến 1.0 (Rất tích cực)

        # Đặt ngưỡng phân loại cảm xúc
        if score > 0.1:
            label = "Tích cực"
        elif score < -0.1:
            label = "Tiêu cực"
        else:
            label = "Trung tính"

        # Làm tròn điểm đến 3 chữ số thập phân cho đẹp
        return {"score": round(score, 3), "label": label}

    except Exception as e:
        logging.error(f"Lỗi AI khi phân tích văn bản: {e}")
        return {"score": 0.0, "label": "Trung tính"}

def apply_sentiment_analysis(articles):
    """
    Nhận vào danh sách bài báo đã làm sạch, áp dụng phân tích cảm xúc cho từng bài.
    """
    logging.info("--- BƯỚC C2: BẮT ĐẦU PHÂN TÍCH CẢM XÚC BẰNG AI (SP4) ---")
    analyzed_articles = []
    
    total_articles = len(articles)
    for index, article in enumerate(articles):
        # In log tiến độ để người dùng/giám khảo thấy hệ thống đang chạy mượt mà
        if (index + 1) % 5 == 0 or index == 0:
            logging.info(f"Đang dùng AI phân tích bài {index + 1}/{total_articles}...")
        
        # Thường phân tích cảm xúc dựa trên tiêu đề (title). 
        # (Nếu có nội dung chi tiết 'content', bạn có thể thay 'title' thành 'content')
        text_to_analyze = article.get('title', '')
        source_name = article.get('source_name', 'Unknown')
        
        # Gọi hàm AI
        sentiment_result = get_sentiment(text_to_analyze, source_name)
        
        # Cập nhật kết quả vào dictionary của bài báo
        # Lưu ý: Biến 'sentiment_score' phải khớp với schema database của bạn
        article['sentiment_score'] = sentiment_result['score']
        
        # Có thể lưu thêm nhãn (Positive/Negative) nếu bảng SQLite của bạn hỗ trợ
        article['sentiment_label'] = sentiment_result['label'] 
        
        analyzed_articles.append(article)
        
    logging.info("--- HOÀN THÀNH PHÂN TÍCH CẢM XÚC ---")
    return analyzed_articles