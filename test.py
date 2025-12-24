import aiohttp
import asyncio


async def get_ip_aiohttp():
    async with aiohttp.ClientSession() as session:
        urls = [
            'https://api.ipify.org',
            'https://ident.me',
            'https://ifconfig.me/ip'
        ]

        for url in urls:
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        ip = (await response.text()).strip()
                        print(f"✅ Ваш IP: {ip} (получен с {url})")
                        return ip
            except Exception as e:
                print(f"❌ Ошибка при запросе к {url}: {e}")
                continue

    print("❌ Не удалось получить IP ни с одного сервиса")
    return None

ip = asyncio.run(get_ip_aiohttp())