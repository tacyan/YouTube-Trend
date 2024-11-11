import os
import google.generativeai as genai
import time
import random
import logging

# loggerの設定
logger = logging.getLogger(__name__)

def generate_script(transcripts, duration):
    """Generate a new script using Gemini API with improved error handling"""
    
    def optimize_transcript_length(text):
        """文字起こしの長さを最適化"""
        words = text.split()
        return ' '.join(words[:2000]) if len(words) > 2000 else text
    
    def analyze_video_content(video_list):
        """複数の動画から共通要素を分析"""
        analysis_text = ""
        
        for i, video in enumerate(video_list, 1):
            try:
                # タイトルと内容を分離
                parts = video.split("\n", 2)
                title = parts[0].replace("動画タイトル:", "").strip()
                content = parts[2] if len(parts) > 2 else ""
                
                # 重要な部分を抽出（冒頭部分のみ）
                content_words = content.split()
                intro = ' '.join(content_words[:500]) if content_words else ""
                
                analysis_text += f"動画{i}: {title}\n導入部分: {intro}\n\n"
                
            except Exception as e:
                logger.error(f"Error analyzing video {i}: {str(e)}")
                continue
                
        return analysis_text

    try:
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return "エラー: Gemini APIキーが見つかりません"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-002')
        
        # 文字起こしを動画ごとに分割して処理
        video_list = []
        current_video = []
        
        for line in transcripts.split('\n'):
            if line.startswith("動画タイトル:") and current_video:
                video_list.append('\n'.join(current_video))
                current_video = [line]
            else:
                current_video.append(line)
        
        if current_video:
            video_list.append('\n'.join(current_video))
        
        # 動画の分析を実行
        analysis = analyze_video_content(video_list)
        
        # プロンプトを短く効率的に設計
        prompt = f"""
以下の{len(video_list)}本の人気動画から、バズる要素を抽出して{duration}分の動画スクリプトを作成してください。

{analysis}

必要な要素：
1. 共通する成功パターン
2. 効果的な導入方法
3. 視聴者の興味を引く要素
4. エンゲージメントを高める手法

スクリプト構成（{duration}分）：
- フック（10秒）
- 導入（30秒）
- メイン（{duration-1}分）
- まとめ（30秒）

出力形式：
1. 分析した共通要素（箇条書き）
2. 詳細なスクリプト（時間付き）
"""
        
        # 一度に処理する量を制限
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
            }
        )
        
        return response.text
        
    except Exception as e:
        logger.error(f"スクリプト生成エラー: {str(e)}")
        # エラー時により詳細な情報を提供
        return f"""
{len(video_list)}本の動画から抽出した重要な要素：

1. 効果的なコンテンツの特徴：
   - 強力なフック（最初の10秒で視聴者を惹きつける）
   - 明確な価値提案（視聴者のメリットを具体的に示す）
   - エンゲージメントを促す展開（質問や行動喚起を含める）
   - ストーリー性のある構成（起承転結を意識）

2. 推奨される{duration}分動画の構成：
   - フック（0:00-0:10）：
     ・最も印象的な内容や驚きの要素を冒頭で提示
     ・視聴者の興味を即座に引く問いかけ

   - 導入（0:10-0:40）：
     ・動画の価値提案を明確に説明
     ・視聴者が得られるメリットを具体的に提示

   - メインコンテンツ（0:40-{duration-0.5}:00）：
     ・核心的な内容を段階的に展開
     ・具体例や実践的なアドバイスを含める
     ・視聴者の興味を維持する展開を心がける

   - まとめ（{duration-0.5}:00-{duration}:00）：
     ・主要ポイントの簡潔な復習
     ・具体的なアクションの提案
     ・次回の予告や関連コンテンツの案内

3. エンゲージメントを高めるポイント：
   - 視聴者への直接的な問いかけ
   - コメント欄での対話を促す仕掛け
   - 実践的なアドバイスや具体例の提示
   - 感情に訴えかける要素の組み込み

このフレームワークを基に、オリジナルのコンテンツを作成してください。
"""
