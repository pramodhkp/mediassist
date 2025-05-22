import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Typography, 
  List, 
  Button, 
  Modal, 
  Form, 
  Input, 
  DatePicker, 
  Select, 
  Spin, 
  message, 
  Popconfirm, 
  Tag, 
  Badge 
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  MedicineBoxOutlined, 
  ClockCircleOutlined, 
  CalendarOutlined 
} from '@ant-design/icons';
import axios from 'axios';
import moment from 'moment';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const MedicationTracker = () => {
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingMedication, setEditingMedication] = useState(null);
  const [form] = Form.useForm();
  const [reminders, setReminders] = useState([]);
  const [loadingReminders, setLoadingReminders] = useState(false);

  // Fetch medications on component mount
  useEffect(() => {
    fetchMedications();
    fetchReminders();
  }, []);

  // Function to fetch medications from the backend
  const fetchMedications = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:12000'}/medications`);
      setMedications(response.data.medications || []);
    } catch (error) {
      console.error('Error fetching medications:', error);
      message.error('Failed to load medications');
    } finally {
      setLoading(false);
    }
  };

  // Function to fetch medication reminders
  const fetchReminders = async () => {
    setLoadingReminders(true);
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:12000'}/medication_reminders?days=7`);
      setReminders(response.data.reminders || []);
    } catch (error) {
      console.error('Error fetching medication reminders:', error);
    } finally {
      setLoadingReminders(false);
    }
  };

  // Handle form submission for adding/editing medication
  const handleFormSubmit = async (values) => {
    try {
      // Format dates for API
      const formattedValues = {
        ...values,
        start_date: values.start_date ? values.start_date.toISOString() : null,
        end_date: values.end_date ? values.end_date.toISOString() : null
      };

      if (editingMedication) {
        // Update existing medication
        await axios.put(`${process.env.REACT_APP_API_URL || 'http://localhost:12000'}/medications/${editingMedication._id}`, formattedValues);
        message.success('Medication updated successfully');
      } else {
        // Add new medication
        await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:12000'}/medications`, formattedValues);
        message.success('Medication added successfully');
      }

      // Reset form and close modal
      form.resetFields();
      setModalVisible(false);
      setEditingMedication(null);

      // Refresh medications list
      fetchMedications();
      fetchReminders();
    } catch (error) {
      console.error('Error saving medication:', error);
      message.error('Failed to save medication');
    }
  };

  // Handle medication deletion
  const handleDelete = async (medicationId) => {
    try {
      await axios.delete(`${process.env.REACT_APP_API_URL || 'http://localhost:12000'}/medications/${medicationId}`);
      message.success('Medication deleted successfully');
      
      // Refresh medications list
      fetchMedications();
      fetchReminders();
    } catch (error) {
      console.error('Error deleting medication:', error);
      message.error('Failed to delete medication');
    }
  };

  // Open modal for editing a medication
  const handleEdit = (medication) => {
    setEditingMedication(medication);
    
    // Set form values
    form.setFieldsValue({
      name: medication.name,
      dosage: medication.dosage,
      frequency: medication.frequency,
      start_date: medication.start_date ? moment(medication.start_date) : null,
      end_date: medication.end_date ? moment(medication.end_date) : null,
      time_of_day: medication.time_of_day || [],
      notes: medication.notes || ''
    });
    
    setModalVisible(true);
  };

  // Open modal for adding a new medication
  const handleAdd = () => {
    setEditingMedication(null);
    form.resetFields();
    setModalVisible(true);
  };

  // Format the date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return moment(dateString).format('MMM D, YYYY');
  };

  // Get tag color based on frequency
  const getFrequencyTagColor = (frequency) => {
    switch (frequency.toLowerCase()) {
      case 'daily':
        return 'blue';
      case 'twice daily':
        return 'purple';
      case 'weekly':
        return 'green';
      case 'monthly':
        return 'orange';
      case 'as needed':
        return 'cyan';
      default:
        return 'default';
    }
  };

  // Render time of day tags
  const renderTimeOfDay = (times) => {
    if (!times || times.length === 0) return <Text type="secondary">No specific times</Text>;
    
    return times.map((time, index) => (
      <Tag key={index} color="blue" style={{ marginRight: '5px', marginBottom: '5px' }}>
        <ClockCircleOutlined /> {time}
      </Tag>
    ));
  };

  return (
    <Card
      title={<Title level={4}>Medication Tracker</Title>}
      className="medication-tracker-card"
      extra={
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleAdd}
        >
          Add Medication
        </Button>
      }
    >
      <Spin spinning={loading}>
        {/* Reminders Section */}
        <div style={{ marginBottom: '20px' }}>
          <Title level={5}>
            <Badge count={reminders.length} style={{ backgroundColor: '#52c41a' }}>
              <span style={{ marginRight: '10px' }}>Upcoming Reminders</span>
            </Badge>
          </Title>
          <Spin spinning={loadingReminders}>
            {reminders.length > 0 ? (
              <List
                size="small"
                dataSource={reminders}
                renderItem={item => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<MedicineBoxOutlined style={{ fontSize: '20px', color: '#1890ff' }} />}
                      title={item.name}
                      description={
                        <>
                          <Text strong>{item.dosage}</Text>
                          {item.time_of_day && item.time_of_day.length > 0 && (
                            <div style={{ marginTop: '5px' }}>
                              {renderTimeOfDay(item.time_of_day)}
                            </div>
                          )}
                        </>
                      }
                    />
                    <div>
                      <Tag color={getFrequencyTagColor(item.frequency)}>
                        {item.frequency}
                      </Tag>
                    </div>
                  </List.Item>
                )}
              />
            ) : (
              <Text type="secondary">No upcoming medication reminders</Text>
            )}
          </Spin>
        </div>

        {/* Medications List */}
        <List
          itemLayout="vertical"
          dataSource={medications}
          locale={{ emptyText: "No medications added yet" }}
          renderItem={item => (
            <List.Item
              actions={[
                <Button 
                  icon={<EditOutlined />} 
                  size="small" 
                  onClick={() => handleEdit(item)}
                />,
                <Popconfirm
                  title="Are you sure you want to delete this medication?"
                  onConfirm={() => handleDelete(item._id)}
                  okText="Yes"
                  cancelText="No"
                >
                  <Button 
                    icon={<DeleteOutlined />} 
                    size="small" 
                    danger 
                  />
                </Popconfirm>
              ]}
            >
              <List.Item.Meta
                avatar={<MedicineBoxOutlined style={{ fontSize: '24px', color: '#1890ff' }} />}
                title={
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span style={{ marginRight: '10px' }}>{item.name}</span>
                    <Tag color={getFrequencyTagColor(item.frequency)}>
                      {item.frequency}
                    </Tag>
                  </div>
                }
                description={
                  <>
                    <div><Text strong>Dosage:</Text> {item.dosage}</div>
                    <div style={{ marginTop: '5px' }}>
                      <Text strong>Schedule:</Text>
                      <div style={{ marginTop: '5px' }}>
                        {renderTimeOfDay(item.time_of_day)}
                      </div>
                    </div>
                  </>
                }
              />
              <div style={{ marginTop: '10px' }}>
                <div>
                  <CalendarOutlined style={{ marginRight: '5px' }} />
                  <Text type="secondary">
                    Start: {formatDate(item.start_date)} 
                    {item.end_date && ` • End: ${formatDate(item.end_date)}`}
                  </Text>
                </div>
                {item.notes && (
                  <div style={{ marginTop: '5px' }}>
                    <Text type="secondary">{item.notes}</Text>
                  </div>
                )}
              </div>
            </List.Item>
          )}
        />
      </Spin>

      {/* Add/Edit Medication Modal */}
      <Modal
        title={editingMedication ? "Edit Medication" : "Add Medication"}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingMedication(null);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleFormSubmit}
          initialValues={{
            time_of_day: [],
            frequency: 'Daily'
          }}
        >
          <Form.Item
            name="name"
            label="Medication Name"
            rules={[{ required: true, message: 'Please enter the medication name' }]}
          >
            <Input placeholder="Enter medication name" />
          </Form.Item>

          <Form.Item
            name="dosage"
            label="Dosage"
            rules={[{ required: true, message: 'Please enter the dosage' }]}
          >
            <Input placeholder="e.g., 10mg, 1 tablet, etc." />
          </Form.Item>

          <Form.Item
            name="frequency"
            label="Frequency"
            rules={[{ required: true, message: 'Please select the frequency' }]}
          >
            <Select placeholder="Select frequency">
              <Option value="Daily">Daily</Option>
              <Option value="Twice Daily">Twice Daily</Option>
              <Option value="Weekly">Weekly</Option>
              <Option value="Monthly">Monthly</Option>
              <Option value="As Needed">As Needed</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="time_of_day"
            label="Time of Day"
          >
            <Select 
              mode="multiple" 
              placeholder="Select time(s) of day"
              optionLabelProp="label"
            >
              <Option value="Morning" label="Morning">Morning (8:00 AM)</Option>
              <Option value="Noon" label="Noon">Noon (12:00 PM)</Option>
              <Option value="Afternoon" label="Afternoon">Afternoon (2:00 PM)</Option>
              <Option value="Evening" label="Evening">Evening (6:00 PM)</Option>
              <Option value="Night" label="Night">Night (10:00 PM)</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="start_date"
            label="Start Date"
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="end_date"
            label="End Date (Optional)"
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="notes"
            label="Notes (Optional)"
          >
            <TextArea rows={4} placeholder="Add any additional notes or instructions" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ marginRight: '10px' }}>
              {editingMedication ? 'Update' : 'Add'}
            </Button>
            <Button onClick={() => {
              setModalVisible(false);
              setEditingMedication(null);
              form.resetFields();
            }}>
              Cancel
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default MedicationTracker;