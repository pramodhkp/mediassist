import React, { useState, useEffect } from 'react';
import { Modal, List, Typography, Spin, Empty, Card, Tag, Divider } from 'antd';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;

const AnalysisResultsModal = ({ visible, onClose }) => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [reportContent, setReportContent] = useState(null);
  const [loadingContent, setLoadingContent] = useState(false);

  // Fetch reports when modal becomes visible
  useEffect(() => {
    if (visible) {
      fetchReports();
    }
  }, [visible]);

  // Fetch the list of analysis reports
  const fetchReports = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/analysis_reports');
      setReports(response.data.reports || []);
    } catch (error) {
      console.error('Error fetching analysis reports:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch a specific report's content
  const fetchReportContent = async (reportId) => {
    setLoadingContent(true);
    try {
      const response = await axios.get(`http://localhost:5000/analysis_report/${reportId}`);
      setReportContent(response.data.report);
    } catch (error) {
      console.error('Error fetching report content:', error);
    } finally {
      setLoadingContent(false);
    }
  };

  // Handle report selection
  const handleReportSelect = (report) => {
    setSelectedReport(report);
    fetchReportContent(report.report_id);
  };

  // Format the timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown date';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Render JSON content in a readable format
  const renderContent = (content) => {
    if (!content) return <Empty description="No content available" />;
    
    try {
      // If content is a JSON string, parse it
      const parsedContent = typeof content === 'string' ? JSON.parse(content) : content;
      
      if (typeof parsedContent === 'object') {
        return (
          <div>
            {parsedContent.summary && (
              <>
                <Title level={4}>Summary</Title>
                <Paragraph>{parsedContent.summary}</Paragraph>
                <Divider />
              </>
            )}
            
            {parsedContent.key_findings && parsedContent.key_findings.length > 0 && (
              <>
                <Title level={4}>Key Findings</Title>
                <List
                  itemLayout="vertical"
                  dataSource={parsedContent.key_findings}
                  renderItem={item => (
                    <List.Item>
                      <Card
                        size="small"
                        title={item.finding}
                        extra={<Tag color="blue">Action Required</Tag>}
                      >
                        <Paragraph><strong>Significance:</strong> {item.significance}</Paragraph>
                        <Paragraph><strong>Action Item:</strong> {item.action_item}</Paragraph>
                      </Card>
                    </List.Item>
                  )}
                />
                <Divider />
              </>
            )}
            
            {parsedContent.health_concerns && parsedContent.health_concerns.length > 0 && (
              <>
                <Title level={4}>Health Concerns</Title>
                <List
                  itemLayout="vertical"
                  dataSource={parsedContent.health_concerns}
                  renderItem={item => (
                    <List.Item>
                      <Card 
                        size="small" 
                        title={item.concern}
                        extra={
                          <Tag color={
                            item.risk_level === 'High' ? 'red' : 
                            item.risk_level === 'Medium' ? 'orange' : 'green'
                          }>
                            {item.risk_level} Risk
                          </Tag>
                        }
                      >
                        <Paragraph><strong>Explanation:</strong> {item.explanation}</Paragraph>
                        <Paragraph><strong>Action Item:</strong> {item.action_item}</Paragraph>
                      </Card>
                    </List.Item>
                  )}
                />
                <Divider />
              </>
            )}
            
            {parsedContent.recommendations && parsedContent.recommendations.length > 0 && (
              <>
                <Title level={4}>Recommendations</Title>
                <List
                  itemLayout="vertical"
                  dataSource={parsedContent.recommendations}
                  renderItem={item => (
                    <List.Item>
                      <Card 
                        size="small" 
                        title={item.action}
                        extra={
                          <Tag color={
                            item.priority === 'High' ? 'red' : 
                            item.priority === 'Medium' ? 'orange' : 'green'
                          }>
                            {item.priority} Priority
                          </Tag>
                        }
                      >
                        <Paragraph><strong>Explanation:</strong> {item.explanation}</Paragraph>
                        <Paragraph><strong>How To Implement:</strong> {item.how_to}</Paragraph>
                      </Card>
                    </List.Item>
                  )}
                />
                <Divider />
              </>
            )}
            
            {parsedContent.lifestyle_suggestions && parsedContent.lifestyle_suggestions.length > 0 && (
              <>
                <Title level={4}>Lifestyle Suggestions</Title>
                <List
                  itemLayout="vertical"
                  dataSource={parsedContent.lifestyle_suggestions}
                  renderItem={item => (
                    <List.Item>
                      <Card size="small" title={item.category}>
                        <Paragraph><strong>Suggestion:</strong> {item.suggestion}</Paragraph>
                        <Paragraph><strong>Easy Implementation:</strong> {item.easy_implementation}</Paragraph>
                      </Card>
                    </List.Item>
                  )}
                />
                <Divider />
              </>
            )}
            
            {parsedContent.terminology_explained && parsedContent.terminology_explained.length > 0 && (
              <>
                <Title level={4}>Medical Terminology Explained</Title>
                <List
                  itemLayout="vertical"
                  dataSource={parsedContent.terminology_explained}
                  renderItem={item => (
                    <List.Item>
                      <Card size="small" title={item.term}>
                        <Paragraph><strong>Explanation:</strong> {item.explanation}</Paragraph>
                        <Paragraph><strong>Why It Matters:</strong> {item.why_it_matters}</Paragraph>
                      </Card>
                    </List.Item>
                  )}
                />
                <Divider />
              </>
            )}
            
            {parsedContent.next_steps && parsedContent.next_steps.length > 0 && (
              <>
                <Title level={4}>Next Steps</Title>
                <List
                  itemLayout="vertical"
                  dataSource={parsedContent.next_steps}
                  renderItem={(step, index) => (
                    <List.Item>
                      <Card size="small" title={`Step ${index + 1}`}>
                        <Paragraph>{step}</Paragraph>
                      </Card>
                    </List.Item>
                  )}
                />
                <Divider />
              </>
            )}
            
            {parsedContent.additional_insights && (
              <>
                <Title level={4}>Additional Insights</Title>
                <Paragraph>{parsedContent.additional_insights}</Paragraph>
              </>
            )}
          </div>
        );
      }
    } catch (e) {
      // If parsing fails, display as plain text
      console.error("Error parsing content:", e);
    }
    
    // Fallback to displaying as plain text
    return <Paragraph>{content}</Paragraph>;
  };

  return (
    <Modal
      title="Analysis Results"
      open={visible}
      onCancel={onClose}
      width={1000}
      footer={null}
    >
      <div style={{ display: 'flex', height: '70vh' }}>
        {/* Left sidebar with report list */}
        <div style={{ width: '30%', borderRight: '1px solid #f0f0f0', paddingRight: '16px', overflowY: 'auto' }}>
          <Spin spinning={loading}>
            <List
              itemLayout="vertical"
              dataSource={reports}
              locale={{ emptyText: "No analysis reports found" }}
              renderItem={report => (
                <List.Item 
                  onClick={() => handleReportSelect(report)}
                  style={{ 
                    cursor: 'pointer',
                    backgroundColor: selectedReport && selectedReport.report_id === report.report_id ? '#f0f0f0' : 'transparent'
                  }}
                >
                  <List.Item.Meta
                    title={`Analysis Report (${report.file_count} files)`}
                    description={formatTimestamp(report.timestamp)}
                  />
                  {report.filenames && report.filenames.length > 0 && (
                    <div>
                      <Text type="secondary">Files: </Text>
                      <Text type="secondary">{report.filenames.join(', ')}</Text>
                    </div>
                  )}
                </List.Item>
              )}
            />
          </Spin>
        </div>
        
        {/* Right content area with report details */}
        <div style={{ width: '70%', paddingLeft: '16px', overflowY: 'auto' }}>
          <Spin spinning={loadingContent}>
            {selectedReport ? (
              reportContent ? (
                <div>
                  <Title level={3}>Analysis Report</Title>
                  <Paragraph>
                    <Text strong>Date: </Text>
                    <Text>{formatTimestamp(reportContent.timestamp)}</Text>
                  </Paragraph>
                  <Paragraph>
                    <Text strong>Files Analyzed: </Text>
                    <Text>{reportContent.filenames ? reportContent.filenames.join(', ') : 'None'}</Text>
                  </Paragraph>
                  <Divider />
                  {renderContent(reportContent.content)}
                </div>
              ) : (
                <Empty description="Select a report to view details" />
              )
            ) : (
              <Empty description="Select a report to view details" />
            )}
          </Spin>
        </div>
      </div>
    </Modal>
  );
};

export default AnalysisResultsModal;