import React from 'react';
import { List, Button, Card, Space, Typography, Popconfirm } from 'antd';

const { Text, Paragraph } = Typography;

const MedicationList = ({ medications, onEdit, onDelete }) => {
    if (!medications || medications.length === 0) {
        return <Text>No medications found.</Text>;
    }

    return (
        <List
            grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 3, xl: 3, xxl: 4 }}
            dataSource={medications}
            renderItem={med => (
                <List.Item>
                    <Card 
                        title={med.medication_name} 
                        actions={[
                            <Button type="link" onClick={() => onEdit(med)}>Edit</Button>,
                            <Popconfirm
                                title={`Are you sure you want to delete ${med.medication_name}?`}
                                onConfirm={() => onDelete(med._id)}
                                okText="Yes"
                                cancelText="No"
                            >
                                <Button type="link" danger>Delete</Button>
                            </Popconfirm>
                        ]}
                    >
                        {med.dosage && <Paragraph><strong>Dosage:</strong> {med.dosage}</Paragraph>}
                        {med.frequency && <Paragraph><strong>Frequency:</strong> {med.frequency}</Paragraph>}
                        {med.start_date && <Paragraph><strong>Start Date:</strong> {new Date(med.start_date).toLocaleDateString()}</Paragraph>}
                        {med.end_date && <Paragraph><strong>End Date:</strong> {new Date(med.end_date).toLocaleDateString()}</Paragraph>}
                        {med.reminder_times && med.reminder_times.length > 0 && (
                            <Paragraph><strong>Reminders:</strong> {med.reminder_times.join(', ')}</Paragraph>
                        )}
                        {med.notes && <Paragraph><strong>Notes:</strong> {med.notes}</Paragraph>}
                    </Card>
                </List.Item>
            )}
        />
    );
};

export default MedicationList;
```
