import React, { useState, useEffect, useCallback } from 'react';
import { Button, Modal, Typography, message, Spin, Row, Col, Divider } from 'antd';
import MedicationForm from './MedicationForm';
import MedicationList from './MedicationList';
import MedicationReminders from './MedicationReminders';

const { Title } = Typography;

// Assume a fixed user ID for now, as per requirements
const TEMP_USER_ID = "test-user"; 
// Base URL for the API. Configure this properly in a real app.
const API_BASE_URL = 'http://localhost:5000/api';


const MedicationsPage = () => {
    const [medications, setMedications] = useState([]);
    const [dueMedications, setDueMedications] = useState([]);
    const [isFormVisible, setIsFormVisible] = useState(false);
    const [medicationToEdit, setMedicationToEdit] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingDue, setIsLoadingDue] = useState(false);

    const fetchAllMedications = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/medications/${TEMP_USER_ID}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setMedications(data || []);
        } catch (error) {
            message.error(`Failed to fetch medications: ${error.message}`);
            setMedications([]); // Set to empty array on error
        } finally {
            setIsLoading(false);
        }
    }, []);

    const fetchDueMedications = useCallback(async () => {
        setIsLoadingDue(true);
        try {
            const response = await fetch(`${API_BASE_URL}/medications/due/${TEMP_USER_ID}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setDueMedications(data || []);
        } catch (error) {
            message.error(`Failed to fetch due medications: ${error.message}`);
            setDueMedications([]); // Set to empty array on error
        } finally {
            setIsLoadingDue(false);
        }
    }, []);

    useEffect(() => {
        fetchAllMedications();
        fetchDueMedications();
    }, [fetchAllMedications, fetchDueMedications]);

    const showAddForm = () => {
        setMedicationToEdit(null);
        setIsFormVisible(true);
    };

    const showEditForm = (medication) => {
        setMedicationToEdit(medication);
        setIsFormVisible(true);
    };

    const handleFormCancel = () => {
        setIsFormVisible(false);
        setMedicationToEdit(null);
    };

    const handleSaveMedication = async (values, medicationId) => {
        const url = medicationId 
            ? `${API_BASE_URL}/medications/${medicationId}` 
            : `${API_BASE_URL}/medications`;
        const method = medicationId ? 'PUT' : 'POST';

        // Ensure user_id is part of the payload, medication_form might not add it if editing
        const payload = { ...values, user_id: TEMP_USER_ID };

        setIsLoading(true);
        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            message.success(`Medication ${medicationId ? 'updated' : 'added'} successfully!`);
            setIsFormVisible(false);
            setMedicationToEdit(null);
            fetchAllMedications(); // Refresh list
            fetchDueMedications(); // Also refresh due medications
        } catch (error) {
            message.error(`Failed to save medication: ${error.message}`);
        } finally {
            // setIsLoading(false); // Already handled by fetchAllMedications
        }
    };

    const handleDeleteMedication = async (medicationId) => {
        setIsLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/medications/${medicationId}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                 const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            message.success('Medication deleted successfully!');
            fetchAllMedications(); // Refresh list
            fetchDueMedications(); // Also refresh due medications
        } catch (error) {
            message.error(`Failed to delete medication: ${error.message}`);
        } finally {
            // setIsLoading(false); // Already handled by fetchAllMedications
        }
    };


    return (
        <div style={{ padding: '20px' }}>
            <Title level={2}>Medication Management</Title>
            
            <Row gutter={[16, 16]}>
                <Col xs={24} md={8}>
                    <Spin spinning={isLoadingDue}>
                         <MedicationReminders userId={TEMP_USER_ID} dueMedications={dueMedications} />
                    </Spin>
                </Col>
                <Col xs={24} md={16}>
                    <Button type="primary" onClick={showAddForm} style={{ marginBottom: '20px' }}>
                        Add New Medication
                    </Button>

                    <Modal
                        title={medicationToEdit ? "Edit Medication" : "Add New Medication"}
                        visible={isFormVisible}
                        footer={null} // Footer is handled by Form's submit button
                        onCancel={handleFormCancel}
                        destroyOnClose // Reset form state when modal is closed
                    >
                        <MedicationForm
                            userId={TEMP_USER_ID}
                            medicationToEdit={medicationToEdit}
                            onSave={handleSaveMedication}
                            onCancel={handleFormCancel}
                        />
                    </Modal>
                    
                    <Divider />
                    <Title level={3}>Your Medications</Title>
                    <Spin spinning={isLoading}>
                        <MedicationList
                            medications={medications}
                            onEdit={showEditForm}
                            onDelete={handleDeleteMedication}
                        />
                    </Spin>
                </Col>
            </Row>
        </div>
    );
};

export default MedicationsPage;
```
