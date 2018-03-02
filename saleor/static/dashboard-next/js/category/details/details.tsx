import * as React from "react";
import { Component, Fragment } from "react";
import { graphql, compose, Mutation, Query } from "react-apollo";

import { ConfirmRemoval } from "../../components/modals";
import { DescriptionCard } from "../../components/cards";
import { categoryDelete } from "../mutations";
import { categoryDetails } from "../queries";
import { pgettext, interpolate, ngettext } from "../../i18n";

interface CategoryPropertiesProps {
  categoryId: string;
}

interface CategoryPropertiesState {
  opened: boolean;
}

class CategoryProperties extends Component<
  CategoryPropertiesProps,
  CategoryPropertiesState
> {
  state = { opened: false };

  handleRemoveButtonClick = () => {
    this.setState({ opened: false });
  };

  render() {
    const { categoryId } = this.props;
    const titleFmt = pgettext(
      "Remove category modal title",
      "Remove category %s"
    );
    const contentFmt = pgettext(
      "Remove category modal title",
      "Are you sure you want to remove category <strong>%s</strong>?"
    );
    return (
      <Query query={categoryDetails} variables={{ id: categoryId }}>
        {({ data }) => {
          if (data.loading) {
            return <span>loading</span>;
          }
          return (
            <Mutation mutation={categoryDelete} variables={{ id: categoryId }}>
              {deleteCategory => {
                const handleRemoveAction = async () => {
                  await deleteCategory();
                  this.handleRemoveButtonClick;
                };

                return (
                  <>
                    <DescriptionCard
                      description={data.category.description}
                      handleEditButtonClick={handleRemoveAction}
                      handleRemoveButtonClick={this.handleRemoveButtonClick}
                      title={data.category.name}
                    />
                    <ConfirmRemoval
                      onClose={this.handleRemoveButtonClick}
                      onConfirm={handleRemoveAction}
                      opened={this.state.opened}
                      title={interpolate(titleFmt, [data.category.name])}
                    >
                      <p
                        dangerouslySetInnerHTML={{
                          __html: interpolate(contentFmt, [data.category.name])
                        }}
                      />
                      {data.category.products &&
                        data.category.products.totalCount > 0 && (
                          <p>
                            {interpolate(
                              ngettext(
                                "There is one product in this category that will be removed.",
                                "There are %s products in this category that will be removed.",
                                data.category.products.totalCount
                              ),
                              [data.category.products.totalCount]
                            )}
                          </p>
                        )}
                    </ConfirmRemoval>
                  </>
                );
              }}
            </Mutation>
          );
        }}
      </Query>
    );
  }
}

export default CategoryProperties;
