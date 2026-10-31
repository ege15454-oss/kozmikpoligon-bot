# Ortak cevap mantığı: Discord ve WhatsApp botları bunu kullanır.
KB = [
    (["merhaba", "selam", "hey", "slm"], "Merhaba! KozmikPoligon YT botuyum. Kanal, VRChat, videolar ya da destek hakkında sorabilirsin."),
    (["kanal", "hakkında", "kimsin", "nedir"], "KozmikPoligon YT, oyun ve VRChat içerikleri olan eğlenceli bir YouTube kanalı."),
    (["vrchat", "vr"], "VRChat maceraları, dünyalar ve komik anlar kanalın en büyük parçası."),
    (["oyun"], "VRChat dışında farklı oyunlardan da eğlenceli videolar çekiyoruz."),
    (["video", "yeni", "ne zaman"], "Düzenli olarak yeni videolar geliyor. Abone ol ve zil simgesine bas!"),
    (["abone", "takip"], "Abone olup zili açarsan yeni videolardan ilk sen haberdar olursun."),
    (["destek", "iletişim", "yardım", "iş birliği"], "Soru, öneri ve iş birliği için kozmikpoligonytsupport hesabından bize ulaşabilirsin."),
]
FALLBACK = "Bunu anlayamadım. Kanal, VRChat, videolar ya da destek hakkında sorabilirsin."

def reply(text: str) -> str:
    t = text.replace("İ", "i").replace("I", "ı").lower()
    for keys, answer in KB:
        if any(k in t for k in keys):
            return answer
    return FALLBACK
