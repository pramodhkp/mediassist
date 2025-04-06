import React, { useState, useEffect } from 'react';
import { Card, Upload, Button, List, Typography, message, Spin, Space } from 'antd';
import { UploadOutlined, FileOutlined, DeleteOutlined, DownloadOutlined, ExperimentOutlined, FileSearchOutlined } from '@ant-design/icons';
import AnalysisResultsModal from './AnalysisResultsModal';
import axios from 'axios';

const { Title } = Typography;

const MedicalReports = () => {
  const [fileList, setFileList] = useState([]);
  const [analyzingFiles, setAnalyzingFiles] = useState(false);
  const [loading, setLoading] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [currentAnalysisId, setCurrentAnalysisId] = useState(null);
  const [statusPollingInterval, setStatusPollingInterval] = useState(null);
  const [resultsModalVisible, setResultsModalVisible] = useState(false);

  // Fetch the list of medical reports on component mount
  useEffect(() => {
    fetchMedicalReports();
    
    // Clean up any polling interval on unmount
    // eslint-disable-next-line react-hooks/exhaustive-deps
    return () => {
      if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
      }
    };
  }, []);

  // Function to fetch medical reports from the backend
  const fetchMedicalReports = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/medical_reports');
      setFileList(response.data.reports || []);
    } catch (error) {
      console.error('Error fetching medical reports:', error);
      message.error('Failed to load medical reports');
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload
  const handleUpload = async (options) => {
    const { file, onSuccess, onError } = options;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post('http://localhost:5000/upload_medical_report', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      onSuccess(response, file);
      message.success(`${file.name} uploaded successfully`);
      
      // Refresh the file list
      fetchMedicalReports();
    } catch (error) {
      console.error('Error uploading file:', error);
      onError(error);
      message.error(`${file.name} upload failed`);
    }
  };
  
  // Poll for analysis status
  const pollAnalysisStatus = (analysisId) => {
    // Clear any existing interval
    if (statusPollingInterval) {
      clearInterval(statusPollingInterval);
    }
    
    // Set up new polling interval
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`http://localhost:5000/analysis_status/${analysisId}`);
        const status = response.data.status;
        
        if (status === 'completed' || status === 'completed_no_content') {
          // Analysis completed successfully
          clearInterval(interval);
          setStatusPollingInterval(null);
          setCurrentAnalysisId(null);
          setAnalyzingFiles(false);
          
          message.success('Deep analysis completed successfully!');
          
          // Optionally open the results modal
          setResultsModalVisible(true);
        } else if (status === 'error') {
          // Analysis failed
          clearInterval(interval);
          setStatusPollingInterval(null);
          setCurrentAnalysisId(null);
          setAnalyzingFiles(false);
          
          message.error(`Analysis failed: ${response.data.error || 'Unknown error'}`);
        }
        // If status is still 'running', continue polling
      } catch (error) {
        console.error('Error polling analysis status:', error);
        // Don't stop polling on network errors, it might be temporary
      }
    }, 2000); // Poll every 2 seconds
    
    setStatusPollingInterval(interval);
  };

  // Handle deep analysis for all files
  const handleDeepAnalysis = async () => {
    if (fileList.length === 0) {
      message.warning('No medical reports available for analysis');
      return;
    }
    
    try {
      // Set analyzing state
      setAnalyzingFiles(true);
      
      const response = await axios.post('http://localhost:5000/deep_analysis');
      
      if (response.data.success) {
        message.success(`Deep analysis started for ${response.data.file_count} files`);
        
        // Start polling for status
        setCurrentAnalysisId(response.data.analysis_id);
        pollAnalysisStatus(response.data.analysis_id);
      } else {
        message.error('Failed to start deep analysis');
        setAnalyzingFiles(false);
      }
    } catch (error) {
      console.error('Error triggering deep analysis:', error);
      message.error('Failed to start deep analysis');
      setAnalyzingFiles(false);
    }
  };

  // Handle file download
  const handleDownload = async (fileId, fileName) => {
    try {
      const response = await axios.get(`http://localhost:5000/download_medical_report/${fileId}`, {
        responseType: 'blob'
      });
      
      // Create a download link and trigger the download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      message.success(`${fileName} downloaded successfully`);
    } catch (error) {
      console.error('Error downloading file:', error);
      message.error(`Failed to download ${fileName}`);
    }
  };

  // Handle file deletion
  const handleDelete = async (fileId) => {
    try {
      await axios.delete(`http://localhost:5000/delete_medical_report/${fileId}`);
      message.success('File deleted successfully');
      
      // Refresh the file list
      fetchMedicalReports();
    } catch (error) {
      console.error('Error deleting file:', error);
      message.error('Failed to delete file');
    }
  };

  return (
    <Card
      title={<Title level={4}>Medical Reports</Title>}
      className="medical-reports-card"
    >
      <div style={{ marginBottom: '16px' }}>
        <Space>
          <Button
            icon={<ExperimentOutlined />}
            type="primary"
            onClick={handleDeepAnalysis}
            loading={analyzingFiles}
            disabled={fileList.length === 0}
          >
            Deep Analysis
          </Button>
          <Button
            icon={<FileSearchOutlined />}
            onClick={() => setResultsModalVisible(true)}
          >
            Show Results
          </Button>
          <Upload
            customRequest={handleUpload}
            showUploadList={false}
          >
            <Button icon={<UploadOutlined />}>Upload</Button>
          </Upload>
        </Space>
      </div>
      <Spin spinning={loading}>
        <List
          itemLayout="horizontal"
          dataSource={fileList}
          locale={{ emptyText: "No medical reports uploaded yet" }}
          renderItem={item => (
            <List.Item
              actions={[
                <Button
                  icon={<DownloadOutlined />}
                  size="small"
                  onClick={() => handleDownload(item._id, item.filename)}
                />,
                <Button
                  icon={<DeleteOutlined />}
                  size="small"
                  danger
                  onClick={() => handleDelete(item._id)}
                />
              ]}
            >
              <List.Item.Meta
                avatar={<FileOutlined style={{ fontSize: '24px' }} />}
                title={item.filename}
                description={`Uploaded on: ${new Date(item.uploadDate).toLocaleString()}`}
              />
            </List.Item>
          )}
        />
      </Spin>
      
      {/* Analysis Results Modal */}
      <AnalysisResultsModal
        visible={resultsModalVisible}
        onClose={() => setResultsModalVisible(false)}
      />
    </Card>
  );
};

export default MedicalReports;