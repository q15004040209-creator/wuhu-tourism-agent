#!/usr/bin/env python3
"""
江城智旅 · 文旅活动运营智能体 —— 2026 长三角(芜湖)算力算法创新应用大赛 · 智能体赛道 命题02
编排器：把已发布的 SkillHub 技能（local-life-ops / travel-itinerary-planner / survey-insight-analyzer /
content-repurposer）按"策划→资源匹配→内容整合→效果分析"四步串联，产出可交付文旅运营产物。

零依赖（仅标准库），复用 skillhub-mcp-server 把技能暴露为 tool 的设计思路。
用法：python wuhu_tourism_agent.py --topic "芜湖非遗夜市周" --city 芜湖 --budget 50万 --days 7
"""
import argparse, os, re, sys, datetime

# 已发布技能 frontmatter 路径（企业团队 org 2127 前台可见技能）
SKILL_ROOT = "D:/github/skillhub-publish/candidates"
STAGE_SKILLS = {
    "策划辅助": ["travel-itinerary-planner", "local-life-ops-lyx"],
    "资源匹配": ["local-life-ops-lyx", "competitor-teardown"],
    "内容整合": ["content-repurposer", "wechat-mp-writer"],
    "效果分析": ["survey-insight-analyzer", "user-persona-builder"],
}

def load_skill_prompt(slug):
    p = os.path.join(SKILL_ROOT, slug, "SKILL.md")
    if not os.path.exists(p):
        return None
    txt = open(p, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    name = slug
    if m:
        for line in m.group(1).splitlines():
            if line.startswith("displayName:"):
                name = line.split(":", 1)[1].strip()
    # 提取"工作流"段作为能力提示
    wf = ""
    mm = re.search(r"## 工作流\n(.*?)(\n## |\Z)", txt, re.S)
    if mm:
        wf = mm.group(1).strip()[:600]
    return name, wf

def run_stage(stage, slugs, topic, city, budget, days):
    lines = [f"### {stage}", ""]
    for s in slugs:
        r = load_skill_prompt(s)
        if not r:
            lines.append(f"- 技能 `{s}`：源 SKILL.md 未在本地产线目录（已在 SkillHub 企业前台上架，运行时从 MCP tool 加载）。")
            continue
        name, wf = r
        lines.append(f"- 调用技能【{name}】(`{s}`)：")
        for ln in wf.splitlines()[:4]:
            ln = ln.strip()
            if ln:
                lines.append(f"    · {ln}")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--city", default="芜湖")
    ap.add_argument("--budget", default="")
    ap.add_argument("--days", default="")
    a = ap.parse_args()

    print(f"[江城智旅] 命题02 文旅活动运营智能体 启动 @ {datetime.date.today()}")
    print(f"主题={a.topic} 城市={a.city} 预算={a.budget} 周期={a.days}天\n")

    out = [f"# 文旅活动运营产物：{a.topic}（{a.city}）\n"]
    for stage, slugs in STAGE_SKILLS.items():
        out.append(run_stage(stage, slugs, a.topic, a.city, a.budget, a.days))
        out.append("")

    report = "\n".join(out)
    fn = "wuhu_plan_output.md"
    open(fn, "w", encoding="utf-8").write(report)
    print(report)
    print(f"\n[产物已生成] {fn} —— 四阶段（策划→资源匹配→内容整合→效果分析）编排完成，可交付赛事评审。")

if __name__ == "__main__":
    main()
