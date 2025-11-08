import json
import re
from typing import List
import requests
from bs4 import BeautifulSoup


def fetch_episode(link: str) -> List[dict]:
    """위키피디아의 에피소드 데이터 수집하기"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(link, headers=headers)
    
    soup = BeautifulSoup(response.text, "html.parser")
    # 모든 에피소드 테이블 찾기
    tables = soup.select("table.wikitable.plainrowheaders.wikiepisodetable")
    
    all_episodes = []
    
    for table_idx, table in enumerate(tables):
        # 테이블 앞의 헤딩을 찾아서 시즌 정보 추출
        prev_heading = table.find_previous(["h2", "h3"])
        season_name = "Unknown"
        if prev_heading:
            heading_text = prev_heading.get_text(strip=True)
            # "Clannad" 또는 "Clannad After Story" 구분
            if "After Story" in heading_text:
                season_name = "After Story"
            elif "Clannad" in heading_text and "After Story" not in heading_text:
                season_name = "Season 1"
            else:
                season_name = heading_text
        
        episodes = []
        rows = table.select("tr.vevent.module-episode-list-row")
        
        for i, row in enumerate(rows, start=1):
            synopsis = None
            synopsis_row = row.find_next_sibling("tr", class_="expand-child")
            if synopsis_row:
                synopsis_cell = synopsis_row.select_one("td.description div.shortSummaryText")
                synopsis = synopsis_cell.get_text(strip=True) if synopsis_cell else None
            
            episodes.append({
                "season": season_name,
                "episode_in_season": i,
                "synopsis": synopsis,
            })
        
        all_episodes.extend(episodes)
        print(f"Found {len(episodes)} episodes from {season_name}")
    
    return all_episodes


def main() -> None:
    """여러 시즌의 에피소드를 가져와서 하나의 JSON 파일로 데이터 수집"""
    episode_links = [
        "https://en.wikipedia.org/wiki/List_of_Clannad_episodes" ## 클라나드 1기 + After Story
    ]
    
    all_episodes = []
    for link in episode_links:
        episodes = fetch_episode(link)
        all_episodes.extend(episodes)
    
    output_file = "output/1_원본데이터.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_episodes, f, indent=2, ensure_ascii=False)
    
    print(f"데이터 수집이 완료되었습니다. 총 {len(all_episodes)}개의 에피소드를 수집했습니다.")


if __name__ == "__main__":
    main()