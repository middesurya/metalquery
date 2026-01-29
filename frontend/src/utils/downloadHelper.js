import html2canvas from 'html2canvas';

/**
 * Downloads an image from a URL or Base64 string by fetching it as a Blob.
 * This solves cross-origin issues and ensures the browser respects the download attribute.
 * @param {string} url - The URL or Base64 data of the image.
 * @param {string} filename - The desired filename for the download.
 */
export const downloadImage = async (url, filename) => {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Clean up the object URL to release memory
        setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
        console.error('Download failed:', error);
        alert('Failed to download image. Please try opening it in a new tab.');
    }
};

/**
 * Exports a DOM element as a PNG image using html2canvas.
 * @param {HTMLElement} element - The DOM element to capture.
 * @param {string} filename - The desired filename.
 */
export const exportElementAsImage = async (element, filename) => {
    if (!element) return;

    try {
        const canvas = await html2canvas(element, {
            backgroundColor: '#1e293b', // Match the dark theme background
            logging: false,
            useCORS: true // vital for images inside the element
        });

        const dataUrl = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error('Export failed:', error);
        alert('Failed to export chart.');
    }
};
