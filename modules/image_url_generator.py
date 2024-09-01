import os
import shutil
from urllib.parse import quote

def generate_image_urls_and_archive(img_dir, archive_dir, base_url, output_file, only_latest=False):
    # 画像フォルダが存在するか確認
    if not os.path.exists(img_dir):
        raise ValueError(f"画像フォルダが見つかりません: {img_dir}")

    # アーカイブフォルダが存在しない場合は作成
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    # 画像ファイルリストを取得
    image_files = sorted(
        [f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))],
        key=lambda x: os.path.getmtime(os.path.join(img_dir, x)),
        reverse=True
    )

    # 最新の画像のみ処理する場合
    if only_latest and image_files:
        image_files = [image_files[0]]

    image_urls = []
    for img_file in image_files:
        img_path = os.path.join(img_dir, img_file)
        archive_path = os.path.join(archive_dir, img_file)

        # URLを生成
        image_url = f"{base_url}{quote(img_file)}"
        image_urls.append(image_url)

        # 画像をアーカイブフォルダに移動
        shutil.move(img_path, archive_path)

    # 結果をファイルに書き込む
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(image_urls))

    return image_urls
