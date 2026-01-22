from flask import jsonify, send_from_directory
import os
from pathlib import Path

class AssetController:
    @staticmethod
    def serve_uploaded_file(filename):
        """Serve files from the uploads directory with security checks"""
        try:
            # Define the base upload directory
            upload_folder = 'uploads'

            # Security: Prevent path traversal attacks
            # Ensure filename doesn't contain .. or absolute paths
            if '..' in filename or filename.startswith('/'):
                return jsonify({'error': 'Invalid filename'}), 403

            # Construct the full path
            file_path = os.path.join(upload_folder, filename)

            # Additional security: Ensure the resolved path is still within uploads directory
            upload_folder_abs = os.path.abspath(upload_folder)
            file_path_abs = os.path.abspath(file_path)

            if not file_path_abs.startswith(upload_folder_abs):
                return jsonify({'error': 'Access denied'}), 403

            # Check if file exists
            if not os.path.exists(file_path_abs):
                return jsonify({'error': 'File not found'}), 404

            # Serve the file
            # Determine the directory and filename for send_from_directory
            directory = os.path.dirname(file_path_abs)
            filename_only = os.path.basename(file_path_abs)

            return send_from_directory(
                directory,
                filename_only,
                as_attachment=False  # Display in browser if possible
            )

        except Exception as e:
            return jsonify({'error': f'Error serving file: {str(e)}'}), 500
