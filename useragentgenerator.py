# 100 farklı iOS User-Agent oluşturmak için çeşitli sürüm, cihaz ve browser varyasyonlarını karıştıracağız.
from random import choice, randint

ios_versions = [f"{i}_{j}" for i in range(12, 18) for j in range(0, 5)]
devices = ["iPhone", "iPad", "iPod touch"]
safari_versions = [f"{randint(600, 605)}.1.{randint(1, 20)}" for _ in range(100)]
mobile_versions = [f"{randint(10, 20)}E{randint(100, 999)}" for _ in range(100)]
safari_main_versions = [str(i) for i in range(12, 18)]

user_agents = set()

while len(user_agents) < 100:
    device = choice(devices)
    ios_version = choice(ios_versions)
    safari_build = choice(safari_versions)
    mobile_build = choice(mobile_versions)
    safari_main = choice(safari_main_versions)
    ua = (
        f"Mozilla/5.0 ({device}; CPU {device} OS {ios_version} like Mac OS X) "
        f"AppleWebKit/{safari_build} (KHTML, like Gecko) Version/{safari_main}.0 "
        f"Mobile/{mobile_build} Safari/{safari_build}"
    )
    user_agents.add(ua)

# Sonuçları döndür
list(user_agents)[:100]  # 100 adet UA listesi

