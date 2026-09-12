"""Create additive generator from untouched V2 with explicitly bounded intrados changes."""
from pathlib import Path
SOURCE=Path(__file__).resolve().parent
code=(SOURCE.parent/'BridgeHeroV2/generate_bridge_hero_v2.py').read_text()
code=code.split('# Textured three-quarter inspection')[0]
replacements={
"OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/BridgeHeroV2'":"OUT=SOURCE/'staged'",
"(-2.62,2.62,-7,7,-.22,-.032)":"(-2.62,2.62,-7,7,-.16,-.032)",
"(5.2 if outer else 4.9)":"(6.68 if outer else 6.4)",
"(2.98 if outer else 2.78)":"(2.99 if outer else 2.82)",
"[(4.9,-.15),(-4.9,-.15)]":"[(6.4,-.15),(-6.4,-.15)]",
"(5.2,-3.0)":"(6.68,-3.0)",
"[(-7,-4.9),(4.9,7)]":"[(-7,-6.4),(6.4,7)]",
"2.78*math.sqrt(1-(y/4.9)**2)":"2.82*math.sqrt(1-(y/6.4)**2)",
"'arch_clear_span':9.8":"'arch_clear_span':12.8",
"'arch_crown_below_deck':.22":"'arch_crown_below_deck':.18",
"CW_StoneBridgeHeroV2_14m":"CW_StoneBridgeHeroV3_14m",
"StoneBridgeHeroV2_14m.blend":"StoneBridgeHeroV3_14m.blend",
"SOURCE/'manifest.json'":"SOURCE/'structural-manifest.json'"
}
for old,new in replacements.items():
    assert old in code,old
    code=code.replace(old,new)
code+='\nprint("STRUCTURAL_BRIDGE_V3_STAGED_COMPLETE", manifest["triangles"])\n'
(SOURCE/'generate_structural_v3.py').write_text(code,encoding='utf-8')
