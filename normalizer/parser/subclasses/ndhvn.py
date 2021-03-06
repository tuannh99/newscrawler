#!/usr/bin/python
# -*- coding: utf8 -*-

from copy import deepcopy

# Done
from normalizer.parser import *


class NdhVnParser(SubBaseParser):
    def __init__(self):
        # Bắt buộc phải gọi đầu tiên
        super().__init__()

        # Tên trang web sử dụng kiểu Title Case
        self._source_page = 'Người Đồng Hành'

        # Chứa tên miền không có http://www dùng cho parser tự động nhận dạng
        self._domain = 'ndh.vn'

        # Chứa tên miền đầy đủ và không có / cuối cùng dùng để tìm url tuyệt đối
        self._full_domain = 'http://ndh.vn'

        # Custom các regex dùng để parse một số trang dùng subdomain (ví dụ: *.vnexpress.net)
        # self._domain_regex =

        # THAY ĐỔI CÁC HÀM TRONG VARS ĐỂ THAY ĐỔI CÁC THAM SỐ CỦA HÀM CHA

        # Tìm thẻ chứa tiêu đề
        # Gán bằng con trỏ hàm hoặc biểu thức lambda
        self._vars['get_title_tag_func'] = lambda x: x.find('div', class_='title-detail')

        # Tìm thẻ chứa nội dung tóm tắt
        # Gán bằng con trỏ hàm hoặc biểu thức lambda
        self._vars['get_summary_tag_func'] = lambda x: x.find('div', class_='shapo-detail')

        # Tìm thẻ chứa danh sách các thẻ a chứa keyword bên trong
        # Gán bằng con trỏ hàm hoặc biểu thức lambda
        self._vars['get_tags_tag_func'] = lambda x: x.find('ul', class_='ullinksmall')

        # Tìm thẻ chứa chuỗi thời gian đăng bài
        # Gán bằng con trỏ hàm hoặc biểu thức lambda
        self._vars['get_time_tag_func'] = lambda x: x.find('span', class_='sub-time')

        # Định dạng chuỗi thời gian và trả về đối tượng datetime
        # Gán bằng con trỏ hàm hoặc biểu thức lambda
        def get_datetime_func(string):
            parts = string.split(' ')
            return datetime.strptime('%s %s' % (parts[1], parts[-1]), '%H:%M %d/%m/%Y')

        self._vars['get_datetime_func'] = get_datetime_func

        # Chỉ định các nhãn có khả năng là caption
        # Gán bằng danh sách ['A', 'B', ..., 'Z']
        # Mặc định: ['desc', 'pic', 'img', 'box', 'cap', 'photo', 'hinh', 'anh']
        # self._vars['caption_classes'] =

        # Chỉ định các nhãn có khả năng là author
        # Gán bằng danh sách ['A', 'B', ..., 'Z']
        # Mặc định: ['author', 'copyright', 'source', 'nguon', 'tac-gia', 'tacgia']
        # self._vars['author_classes'] =

        # Chỉ định thẻ chứa nội dung chính
        # Gán bằng con trỏ hàm hoặc biểu thức lambda
        self._vars['get_main_content_tag_func'] = lambda x: x.find('div', class_='main-detail')

        # Chỉ định thẻ chứa tên tác giả
        # Khi sử dụng thẻ này thì sẽ tự động không sử dụng tính năng tự động nhận dạng tên tác giả
        # Gán bằng con trỏ hàm hoặc biểu thức lambda
        self._vars['get_author_tag_func'] = lambda x: x.find('p', class_='name-writer')

        # Chỉ định các nhãn được phép và không được phép dùng để dự đoán author
        # Các nhãn: author, center, right, bold, italic
        # Phân cách nhau bởi dấu | và những nhãn nào không được phép thì có tiền tố ^ ở đầu
        # Ví dụ: 'right|bold|author|^center|^italic'
        # self._vars['author_classes_pattern'] =

        # Chỉ định tự động xóa tất cả các chuỗi bên dưới tác giả
        # Thích hợp khi bài viết chèn nhiều quảng cảo, links bên dưới mà không có id để xóa
        # Gán bằng True / False
        # self._vars['clear_all_below_author'] = True

        # Trả về url chứa hình ảnh thumbnail được lưu ở thẻ bên ngoài nội dung chính
        # Mặc định sẽ tự động nhận dạng
        # Gán bằng con trỏ hàm hoặc biểu thức lambda
        # self._vars['get_thumbnail_url_func'] =

        # Biến vars có thể được sử dụng cho nhiều mục đích khác
        # Tạo bộ parser riêng cho video
        video_parser = deepcopy(self)

        video_parser._vars['get_main_content_tag_func'] = lambda x: x.find('div', id='cne-player')

        video_parser._pre_process = super(NdhVnParser, video_parser)._pre_process

        def post_process_vid(html):
            html.clear()
            html_tag = html.find_parent('html')
            if html_tag is not None:
                # Thumbnail
                image_tag = html_tag.find('link', attrs={'rel': 'image_src', 'href': True})
                thumbnail_url = image_tag.get('href')
                if self._is_valid_image_url(url=thumbnail_url):
                    video_thumbnail_url = thumbnail_url

                # Video URL
                video_tag = html_tag.find('link', attrs={'rel': 'video_src', 'href': True})
                video_url = video_tag.get('href')
                new_video_tag = create_video_tag(src=video_url, thumbnail=video_thumbnail_url,
                                                 mime_type=self._get_mime_type_from_url(url=video_url))
                html.append(new_video_tag)

            return html

        video_parser._post_process = post_process_vid

        video_parser.parse_video = super(NdhVnParser, video_parser)._parse
        self._vars['video_parser'] = video_parser

    # Hàm xử lí video có trong bài, tùy mỗi player mà có cách xử lí khác nhau
    # Khi xử lí xong cần thay thế thẻ đó thành thẻ video theo format qui định
    # Nếu cần tìm link trực tiếp của video trên youtube thì trong helper có hàm hỗ trợ
    # def _handle_video(self, html, default_thumbnail_url=None, timeout=15):
    #     return super()._handle_video(html, default_thumbnail_url, timeout)

    # Sử dụng khi muốn xóa phần tử nào đó trên trang để việc parse được thuận tiện
    def _pre_process(self, html):
        main_html = html.find_parent('html')
        if main_html is not None:
            thumbnail_tag = main_html.find('meta', attrs={'itemprop': 'thumbnailUrl', 'content': True})
            if thumbnail_tag is not None:
                thumbnail_tag.attrs = {'property': 'og:image', 'content': thumbnail_tag.get('content')}

        return super()._pre_process(html)

    # Sử dụng khi muốn xóa phần tử nào đó trên trang để việc parse được thuận tiện
    def _post_process(self, html):
        tags = html.find_all('div', recursive=False)
        for tag in tags:
            content = normalize_string(tag.text)
            if content.startswith('>>') or content.startswith('<<') or content.startswith(
                    'Xem thêm:') or content.startswith('Xem tiếp'):
                tag.decompose()
        return super()._post_process(html)

    def _parse(self, url, html, timeout=15):
        if 'ndh.vn/home.video' in url:
            div_tag = html.find('div', attrs={'class': 'fb-like', 'data-href': True})
            if div_tag is None:
                return None
            video_page_url = div_tag.get('data-href')
            raw_html = self._get_html(url=video_page_url, timeout=timeout)
            if raw_html is None:
                return None
            return self._vars['video_parser'].parse_video(url=video_page_url, html=get_soup(raw_html), timeout=timeout)
        return super()._parse(url, html, timeout)
