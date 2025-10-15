class TenderSearch {
    constructor() {
        this.searchInput = document.getElementById('searchInput');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.searchButton = document.getElementById('searchButton');

        this.initEventListeners();
    }

    initEventListeners() {
        this.searchButton.addEventListener('click', () => this.search());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.search();
        });
    }

    async search() {
        const query = this.searchInput.value.trim();
        if (!query) {
            this.showMessage('请输入搜索关键词');
            return;
        }

        try {
            const response = await fetch(`/api/tenders/search?q=${encodeURIComponent(query)}`);
            const tenders = await response.json();

            this.displayResults(tenders);
        } catch (error) {
            this.showMessage('搜索失败，请重试');
        }
    }

    displayResults(tenders) {
        if (tenders.length === 0) {
            this.resultsContainer.innerHTML = '<p>未找到相关标书</p>';
            return;
        }

        const html = tenders.map(tender => `
            <div class="tender-item">
                <h3>${this.escapeHtml(tender.title)}</h3>
                <p class="description">${this.escapeHtml(tender.description || '暂无描述')}</p>
                <div class="meta">
                    <span>上传者: ${this.escapeHtml(tender.uploader_name || '未知')}</span>
                    <span>文件大小: ${this.formatFileSize(tender.file_size)}</span>
                    <span>下载次数: ${tender.download_count}</span>
                </div>
                <div class="actions">
                    <a href="/api/tenders/${tender.id}/download" class="btn btn-primary">下载</a>
                </div>
            </div>
        `).join('');

        this.resultsContainer.innerHTML = html;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showMessage(message) {
        this.resultsContainer.innerHTML = `<p class="message">${message}</p>`;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new TenderSearch();
});