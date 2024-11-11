import os
import google.generativeai as genai
import time
import random

def generate_script(transcripts, duration):
    """Generate a new script using Gemini API with improved error handling and rate limiting"""
    
    def optimize_transcript_length(text):
        words = text.split()
        return ' '.join(words[:2000]) if len(words) > 2000 else text
    
    def analyze_transcripts(transcripts_list):
        """複数の文字起こしから共通要素を分析"""
        combined_analysis = f"""
以下の{len(transcripts_list)}本の人気動画から共通するバズる要素を分析します：

{transcripts_list}

分析ポイント：
1. 共通するキーワードやフレーズ
2. 導入部の特徴
3. 展開パターン
4. エンゲージメントを高める要素
5. 視聴者の反応が良かったポイント
"""
        return combined_analysis

    max_retries = 5
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                return "エラー: Gemini APIキーが見つかりません"
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-002')
            
            # 文字起こしを配列に分割
            transcript_list = []
            for i, transcript in enumerate(transcripts.split("\n\n"), 1):
                if transcript.startswith("動画タイトル:"):
                    transcript_list.append(f"動画{i}:\n{transcript}")
            
            try:
                analysis = analyze_transcripts(transcript_list)
                prompt = f"""
以下の分析結果から、{duration}分のバズる動画スクリプトを生成してください。

{analysis}

要件：
1. 分析で見つかったバズる要素を必ず含める
2. 以下の構成で作成：
   - フック（最初の10秒）：視聴者を惹きつける強力な導入
   - 導入（30秒）：テーマと価値提案
   - メインコンテンツ（{duration-1}分）：分析で見つかった効果的な要素を組み込む
   - まとめ（30秒）：印象的なエンディング

3. 各セクションで以下を意識：
   - 視聴者の興味を維持する展開
   - エンゲージメントを高める仕掛け
   - 分析で見つかった成功パターンの活用

出力形式：
1. 使用する主なバズる要素（箇条書き）
2. 詳細なスクリプト（時間も記載）

日本語で出力してください。
"""
                
                response = model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.7,
                        'top_p': 0.8,
                        'top_k': 40,
                        'max_output_tokens': 8192,
                    }
                )
                
            except Exception as token_error:
                if "429" in str(token_error):
                    shorter_prompt = f"""
10本の人気動画の分析から、{duration}分のバズる動画スクリプトの要点をまとめてください。

主なポイント：
1. 共通する成功要素
2. 効果的な導入方法
3. コンテンツの展開パターン

構成：
1. フック（10秒）
2. 導入（30秒）
3. メイン（{duration-1}分）
4. まとめ（30秒）
"""
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
                delay = (base_delay * (2 ** attempt)) + (random.random() * 2)
                time.sleep(delay)
                continue
            elif attempt == max_retries - 1:
                return f"""
申し訳ありません。APIの制限により、詳細な分析ができませんでした。

基本的な{duration}分動画の構成案：

1. 共通して効果的だった要素：
   - 強力なフック（最初の10秒）
   - 明確な価値提案
   - エンゲージメントを促す展開

2. 推奨構成：
   - フック（10秒）：視聴者の興味を強く惹く
   - 導入（30秒）：テーマと価値の提示
   - メイン（{duration-1}分）：核心的な内容
   - まとめ（30秒）：印象的なエンディング

※ この構成を参考に、オリジナルのコンテンツを作成してください。
"""
            else:
                return f"スクリプト生成エラー: {str(e)}"
