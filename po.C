#include<stdio.h>
#include<stdib.h>
struct Node{
    int data;
    struct Node*next;
};
struct Node*insertAtBeginning(struct Node*head,int data){
    struct Node*newNode=(struct Node*)malloc(sizeof(struct Node));
    newNode->data=data;
    newNode->next=head;
    return newNode;
}
struct Node*insertAtEnd(struct Node*head,int data){
    struct Node*newNode=(struct Node*)malloc(sizeof(struct Node));
    newNode->data=data;
    newNode->next=NULL;
    if(head==NULL){
        return newNode;
    }
    struct Node*temp=head;
    while(temp->next!=NULL){
        temp=temp->next;
    }
    temp->next=newNode;
    return head;
}
struct Node*insertPos(struct Node*head,int data,int pos){
    struct Node*newNode=(struct Node*)malloc(sizeof(struct Node));
    newNode->data=data;
    if(pos==0){
         newNode->next=head;
         return newNode;
    }
    sruct Node*temp=head;
    for(int i=0;i<pos-1&& temp!=NULL;i++){
        temp=temp->next;
    }
    if(temp==NULL){
        return newNode;
    }
    newNode->next=temp->next;
    temp->next=newNode;
    return head;
}
struct Node*deleteBegin(struct Node*head){
    if(head==NULL){
        return NULL;
    }
    struct Node*temp=head;
    head=head->next;
    free(temp);
    return head;
}
struct Node*deleteEnd(struct Node*head){
    if(head==NULL){
        return NULL;
    }
    if(head->next==NULL){
        free(head);
        return NULL;
    }
    struct Node*temp=head;
    while(temp->next!=NULL){
        temp=temp->next;
    }
    free(temp->next)
    temp->next=NULL;
    return head;
}
struct Node*deleteValue(struct Node*head,int key){
    if(head==NULL){
        return NULL;
    }
    if(head->data==key){
        struct Node*temp=head;
        head=head->next;
        free(head);
        return head;
    }
    struct Node*temp=head;
    while(temp->next!=NULL&&temp->next->data!=key){
        temp=temp->next;
    }
    if(temp->next!=NULL){
        struct Node*del=temp->next;
        temp->next=temp->next->next;
        free(del);
    }
    return head;
}