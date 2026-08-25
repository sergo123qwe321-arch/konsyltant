import unittest
from security_utils import validate_media_url, extract_domain, ALLOWLIST_VIDEO_DOMAINS, ALLOWLIST_IMAGE_DOMAINS, BLOCKED_SHORTENERS

class TestMediaUrlValidation(unittest.TestCase):
    def test_extract_domain(self):
        self.assertEqual(extract_domain("https://rutube.ru/video/123/"), "rutube.ru")
        self.assertEqual(extract_domain("http://www.youtube.com/watch?v=abc"), "youtube.com")
        self.assertEqual(extract_domain("vk.com/video-12345"), "vk.com")
        self.assertEqual(extract_domain("https://avatars.mds.yandex.net/get-image/1"), "avatars.mds.yandex.net")

    def test_video_allowlist(self):
        valid_video_urls = [
            "https://rutube.ru/video/abc123xyz/",
            "https://vkvideo.ru/video-123456_789",
            "https://vk.com/video_ext.php?oid=-123&id=456",
            "https://dzen.ru/video/watch/123456",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://video.yandex.ru/film/123",
            "https://example.com/direct_video.mp4"
        ]
        for url in valid_video_urls:
            is_valid, err = validate_media_url(url, "video")
            self.assertTrue(is_valid, f"Expected valid for {url}, got error: {err}")

    def test_image_allowlist(self):
        valid_image_urls = [
            "https://yandex.ru/images/search?text=test",
            "https://images.yandex.ru/special/1.png",
            "https://avatars.mds.yandex.net/get-dialogs/51080/12345/orig",
            "https://vk.com/photo-123_456",
            "https://pikabu.ru/story/image.jpg",
            "https://imgur.com/gallery/abc",
            "https://i.ibb.co/xyz/pic.jpg",
            "https://cdn.example.org/photo.webp"
        ]
        for url in valid_image_urls:
            is_valid, err = validate_media_url(url, "image")
            self.assertTrue(is_valid, f"Expected valid for {url}, got error: {err}")

    def test_blocked_shorteners(self):
        shorteners = [
            "https://bit.ly/3xyz123",
            "https://tinyurl.com/preview123",
            "https://clck.ru/3ABCDE",
            "https://goo.gl/maps/123",
            "https://t.co/abc12345",
            "https://is.gd/xyz987",
            "https://cutt.ly/sample"
        ]
        for url in shorteners:
            is_valid, err = validate_media_url(url, "image")
            self.assertFalse(is_valid, f"Expected invalid for shortener {url}")
            self.assertIn("сокращения", err)

    def test_dangerous_schemes(self):
        dangerous = [
            "javascript:alert(1)",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "vbscript:msgbox(1)",
            "file:///etc/passwd"
        ]
        for url in dangerous:
            is_valid, err = validate_media_url(url, "image")
            self.assertFalse(is_valid, f"Expected rejected dangerous scheme {url}")
            self.assertIn("опасных схем", err)

    def test_empty_or_invalid_domain(self):
        is_valid, err = validate_media_url("", "image")
        self.assertFalse(is_valid)
        self.assertEqual(err, "URL не может быть пустым")

        is_valid, err = validate_media_url("https://malicious-unverified-site.com/video", "video")
        self.assertFalse(is_valid)
        self.assertIn("Rutube", err)

if __name__ == "__main__":
    unittest.main()
