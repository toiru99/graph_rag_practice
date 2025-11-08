
import json
from typing import List
from utils import  GraphResponse, combine_chunk_graphs, llm_call_structured, UPDATED_TEMPLATE





# 노드 이름 한글 매핑 (귀살대 · 도깨비)
KOREAN_NODE_MAP = {
    # 주요 인물 (Main Characters)
    "Tomoya Okazaki": "오카자키 토모야",
    "Nagisa Furukawa": "후루카와 나기사",
    "Ushio Okazaki": "오카자키 우시오",  # After Story의 핵심 인물 (Tomoya와 Nagisa의 딸)
    "Kyou Fujibayashi": "후지바야시 쿄",
    "Ryou Fujibayashi": "후지바야시 료",
    "Tomoyo Sakagami": "사카가미 토모요",
    "Kotomi Ichinose": "이치노세 코토미",
    "Fuko Ibuki": "이부키 후코",
    "Youhei Sunohara": "스노하라 요헤이",
    
    # 성인 및 부모님 (Adults / Parents)
    "Akio Furukawa": "후루카와 아키오",
    "Sanae Furukawa": "후루카와 사나에",
    "Naoyuki Okazaki": "오카자키 나오유키", # 토모야의 아버지 (이야기 전반에 걸쳐 중요)
    
    # 기타 인물
    "Yusuke Yoshino": "요시노 유스케",
    "Kouko Ibuki": "이부키 코코",
    "Mei Sunohara": "스노하라 메이",

    # 동물 (Animal)
    "Botan": "보탄",

    # 장소 (Location)
    "Hikarizaka High School": "히카리자카 고등학교",
    "Furukawa Bakery": "후루카와 빵집",
    "Club room": "동아리방",
}


if __name__ == "__main__":
    

    with open("output/1_원본데이터.json", encoding="utf-8") as f:
        episodes = json.load(f)

   # 첫 1개 에피소드만 테스트    
    sample_episodes = episodes 
    
    chunk_graphs: List[GraphResponse] = []
    
    for episode in sample_episodes:
        print(f"에피소드 처리 중: 시즌 {episode["season"]}, 에피소드 {episode["episode_in_season"]}")
        
        try:
            # (1) 업데이트된 프롬프트를 반영해서 노드 표준화
            prompt = UPDATED_TEMPLATE + f"\n 입력값\n {episode["synopsis"]}"
            graph_response = llm_call_structured(prompt)

            # (2) 에피소드 번호를 관계에 추가 (ex. S1E01)
            episode_number = f"S{episode['season']}E{episode['episode_in_season']:02d}"

            for relationship in graph_response.relationships:
                if relationship.properties is None:
                    relationship.properties = {}
                relationship.properties["episode_number"] = episode_number
                
            # (3) 노드 이름 한국어로 변환
            for node in graph_response.nodes:
                english_name = node.properties["name"]
                if english_name in KOREAN_NODE_MAP:
                    node.properties["name"] = KOREAN_NODE_MAP[english_name]
            
            chunk_graphs.append(graph_response)
            
        except Exception as e:
            print(f"  - 에피소드 처리 중 오류 발생: {e}")
            continue
    
    if chunk_graphs:
        combined_graph = combine_chunk_graphs(chunk_graphs)
        
        with open("output/지식그래프_최종.json", "w", encoding="utf-8") as f:
            json.dump(combined_graph.model_dump(), f, ensure_ascii=False, indent=2)
    else:
        print("그래프를 성공적으로 추출하지 못했습니다.")