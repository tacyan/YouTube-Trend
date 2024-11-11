import os
import google.generativeai as genai
import time
import random

def generate_script(transcripts, duration):
    """Generate a new script using Gemini API with improved error handling and rate limiting"""
    
    def optimize_transcript_length(text):
        # トークン数を制限（約2000トークンに抑える）
        words = text.split()
        return ' '.join(words[:2000]) if len(words) > 2000 else text
    
    def create_shorter_prompt(text, duration):
        return f"""
        以下の文字起こしから、{duration}分のYouTubeスクリプトのアウトラインを生成:

        {text}

        1. 導入（30秒）
        2. メイン（{duration-1}分）
        3. まとめ（30秒）
        """
    
    max_retries = 5  # リトライ回数を増やす
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                return "エラー: Gemini APIキーが見つかりません"
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-002')
            
            # トークン制限に引っかかった場合のフォールバック処理
            try:
                optimized_transcript = optimize_transcript_length(transcripts)
                prompt = f"""
                以下の動画の文字起こしから、{duration}分のYouTubeスクリプトを生成してください。

                文字起こし:
                {optimized_transcript}

                要件:
                1. トレンド分析: 共通キーワード、効果的な導入部
                2. 導入部（30秒）
                3. メインポイント（{duration-1}分）
                4. まとめ（30秒）

                日本語で出力してください。
                """
                
                response = model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.7,
                        'top_p': 0.8,
                        'top_k': 40,
                        'max_output_tokens': 8192,  # トークン数を削減
                    }
                )
                
            except Exception as token_error:
                # トークン制限エラーの場合、より短いプロンプトで再試行
                if "429" in str(token_error):
                    shorter_prompt = create_shorter_prompt(
                        optimize_transcript_length(transcripts)[:1000], 
                        duration
                    )
                    response = model.generate_content(
                        shorter_prompt,
                        generation_config={
                            'temperature': 0.7,
                            'top_p': 0.8,
                            'top_k': 40,
                            'max_output_tokens': 2000,
                        }
                    )
                else:
                    raise token_error
            
            return response.text
            
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                # 指数バックオフ + ジッター
                delay = (base_delay * (2 ** attempt)) + (random.random() * 2)
                time.sleep(delay)
                continue
            elif attempt == max_retries - 1:
                # 最後の試行でもエラーの場合、基本的な応答を返す
                return f"""
                申し訳ありません。APIの制限により、詳細な分析ができませんでした。
                
                基本的な{duration}分動画の構成案:
                
                1. 導入部（30秒）
                   - 視聴者の興味を引く質問や事実
                   - 動画の目的説明
                
                2. メインコンテンツ（{duration-1}分）
                   - 3-4つの主要ポイント
                   - 具体例や事例
                
                3. まとめ（30秒）
                   - 主要ポイントの復習
                   - コールトゥアクション
                
                ※ この構成を参考に、オリジナルのコンテンツを作成してください。
                """
            else:
                return f"スクリプト生成エラー: {str(e)}"
