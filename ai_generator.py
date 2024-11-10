import os
import google.generativeai as genai

def generate_script(transcript, duration):
    """Generate a new script using Gemini API"""
    
    prompt = f"""
    以下の動画の文字起こしを基に、{duration}分の新しいYouTubeスクリプトを生成してください。
    同じようなトピックを扱いますが、独自の視点で展開します。

    元の文字起こし:
    {transcript[:2000]}  # 文字数制限

    以下の要素を含む魅力的なスクリプトを作成してください:
    1. 注目を集める導入部
    2. メインポイントと重要な学び
    3. 分かりやすい例示と比喩
    4. 効果的なコールトゥアクション
    5. バイラル分析:
       - 視聴回数とエンゲージメント分析
       - タイミング分析
       - コンテンツパターンの認識

    必ず{duration}分で収まるように構成し、日本語で出力してください。
    タイムスタンプは[MM:SS]形式で各セクションの開始時に付けてください。
    """
    
    try:
        # Configure Gemini API
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return "エラー: Gemini APIキーが見つかりません"
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"スクリプト生成エラー: {str(e)}"
